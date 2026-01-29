import asyncio
import random
import time
from collections import defaultdict
from loguru import logger
import sys

# Update sys path to ensure src is importable
# sys.path.append(str(Path(__file__).parent))

import src.utils
from src.utils.output import show_dev_info, show_logo
from src.utils.reader import read_xlsx_accounts
from src.utils.constants import ACCOUNTS_FILE, Account, Task, MAIN_MENU_OPTIONS
import src.model
from src.utils.check_github_version import check_version
from src.model.discord.chatter import DiscordChatter
from src.utils.client import create_client
from src.model.start import Start

# Global locks
account_locks = defaultdict(asyncio.Lock)
guild_locks = defaultdict(asyncio.Lock)

async def start():
    """Hàm chính để khởi động bot (Menu Restore)"""
    show_logo()
    show_dev_info()

    # Check version from GitHub repository
    await check_version("Crazyscholarr", "Autochat_discord")
    print("")

    config = src.utils.get_config()
    
    # --- MENIU RESTORATION ---
    while True:
        print("\n=== MAIN MENU ===")
        for i, option in enumerate(MAIN_MENU_OPTIONS):
            print(f"{i+1}. {option}")
        
        choice = input("\nSelect an option (0 to exit): ").strip()
        
        try:
            if choice == "0":
                logger.info("Exiting...")
                sys.exit(0)
                
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(MAIN_MENU_OPTIONS):
                selected_task = MAIN_MENU_OPTIONS[choice_idx]
                config.TASK = selected_task
                logger.info(f"Selected Task: {selected_task}")
                
                # BRANCH LOGIC
                if selected_task == "AI Chat tự động":
                    # Run the NEW Scheduler
                    await run_scheduler_task(config)
                else:
                    # Run LEGACY features
                    await run_legacy_task(selected_task, config)
                    
            else:
                logger.warning("Invalid option. Please try again.")
        except ValueError:
            logger.warning("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            logger.info("Exiting...")
            sys.exit(0)


async def run_scheduler_task(config):
    """
    Runs the new Task-based Scheduler for AI Chat.
    """
    # Đọc tài khoản từ file XLSX
    all_accounts = read_xlsx_accounts(ACCOUNTS_FILE)

    # Xác định phạm vi tài khoản
    start_index = config.SETTINGS.ACCOUNTS_RANGE[0]
    end_index = config.SETTINGS.ACCOUNTS_RANGE[1]

    if start_index == 0 and end_index == 0:
        if config.SETTINGS.EXACT_ACCOUNTS_TO_USE:
            accounts_to_process = [
                acc for acc in all_accounts
                if acc.index in config.SETTINGS.EXACT_ACCOUNTS_TO_USE
            ]
            logger.info(f"Using specific accounts: {config.SETTINGS.EXACT_ACCOUNTS_TO_USE}")
        else:
            accounts_to_process = all_accounts
    else:
        accounts_to_process = [
            acc for acc in all_accounts if start_index <= acc.index <= end_index
        ]

    if not accounts_to_process:
        logger.error("No accounts found in specified range")
        return

    if not any(account.proxy for account in accounts_to_process):
        logger.error("No proxies found in accounts data")
        return

    # PREPARE CLIENTS/SESSIONS
    account_sessions = {}
    
    async def get_or_create_session(account: Account):
        if account.index not in account_sessions:
             account_sessions[account.index] = await create_client(account.proxy)
        return account_sessions[account.index]

    # INITIALIZE TASKS
    tasks: list[Task] = []
    target_channels = config.AI_CHATTER.CHANNELS
    
    if not target_channels:
        logger.error("No channels configured in AI_CHATTER.CHANNELS (Check config.yaml)")
        return

    logger.info(f"Initializing tasks for {len(accounts_to_process)} accounts x {len(target_channels)} guilds...")

    created_task_keys = set()
    for account in accounts_to_process:
        for channel_config in target_channels:
            try:
                guild_id_int = int(channel_config.GUILD_ID)
            except ValueError:
                channel_id_int = channel_config.GUILD_ID
                continue
            
            task_key = (account.index, guild_id_int)
            if task_key in created_task_keys:
                continue
            created_task_keys.add(task_key)

            task = Task(
                account_id=account.index,
                guild_id=guild_id_int,
                next_run=time.time() + random.uniform(0, 5) 
            )
            setattr(task, '_channel_config', channel_config) 
            setattr(task, '_account', account)
            tasks.append(task)

    logger.info(f"Total unique tasks created: {len(tasks)}")

    # SCHEDULER LOOP
    try:
        while True:
            now = time.time()
            ran_any = False
            
            for task in tasks:
                if not task.running and now >= task.next_run:
                    task.running = True
                    ran_any = True
                    asyncio.create_task(run_task(task, get_or_create_session, config))

            if not ran_any:
                await asyncio.sleep(1) 
            else:
                 await asyncio.sleep(0.1) 

    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
    finally:
        for sess in account_sessions.values():
            await sess.close()


async def run_legacy_task(task_name: str, config):
    """
    Runs legacy tasks using the Start class.
    """
    all_accounts = read_xlsx_accounts(ACCOUNTS_FILE)
    
    # Filter Accounts (Same logic)
    start_index = config.SETTINGS.ACCOUNTS_RANGE[0]
    end_index = config.SETTINGS.ACCOUNTS_RANGE[1]

    if start_index == 0 and end_index == 0:
        if config.SETTINGS.EXACT_ACCOUNTS_TO_USE:
             accounts_to_process = [acc for acc in all_accounts if acc.index in config.SETTINGS.EXACT_ACCOUNTS_TO_USE]
        else:
             accounts_to_process = all_accounts
    else:
        accounts_to_process = [acc for acc in all_accounts if start_index <= acc.index <= end_index]

    logger.info(f"Starting legacy task: {task_name} for {len(accounts_to_process)} accounts")
    
    semaphore = asyncio.Semaphore(config.SETTINGS.THREADS)

    async def worker(account):
        async with semaphore:
            async with account_locks[account.index]: # Reuse lock safety if needed
                start_instance = Start(account, config)
                if await start_instance.initialize():
                    await start_instance.flow()
                    # Close session? Start class inside usually handles session via initialize but might not close it explicitly if it doesnt implement context mgr well.
                    # Creating a new session per task run in legacy mode is acceptable.
                    if start_instance.session:
                        await start_instance.session.close()

    tasks = [worker(acc) for acc in accounts_to_process]
    await asyncio.gather(*tasks)
    logger.success(f"Completed task: {task_name}")


async def run_task(task: Task, session_factory, config):
    """
    Executes a single task (Account + Guild message) with Account Locking.
    """
    account = getattr(task, '_account')
    channel_config = getattr(task, '_channel_config')
    guild_id = task.guild_id
    
    async with account_locks[task.account_id]:
        # Guild Lock: Ensure only 1 account chats in this guild at a time
        async with guild_locks[guild_id]:
            try:
                account_prefix = f"<cyan>Account - {task.account_id}</cyan>"
                logger.opt(colors=True).info(f"{account_prefix} | ▶️ Starting chat in guild <yellow>{guild_id}</yellow>")
                
                session = await session_factory(account)
                
                # --- LOGIC TO SEND MESSAGE ---
                cooldown = 60 

                chatter = DiscordChatter(account, session, config)
                result = await chatter._chat_one_round(channel_config)
                
                if result:
                    pause_range = channel_config.PAUSE_BETWEEN_MESSAGES
                    cooldown = random.randint(pause_range[0], pause_range[1])
                    logger.opt(colors=True).info(
                        f"{account_prefix} | ⏸️ Guild <yellow>{guild_id}</yellow> will run again in {cooldown}s (success)"
                    )
                else:
                    cooldown = random.randint(30, 60) 

            except Exception as e:
                logger.opt(colors=True).error(f"<cyan>[Account - {task.account_id}]</cyan> | Task exception: {e}")
                cooldown = 60 
            finally:
                task.next_run = time.time() + cooldown
                task.running = False
