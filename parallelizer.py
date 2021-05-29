import asyncio 
from datetime import datetime, timedelta
import pathlib 
import sys
from constants import * 
import dataframe_image as dfi
from output_processor import generate_schedule_table
from yapapi import Executor, NoPaymentAccountError, Task, WorkContext, windows_event_loop_fix
from yapapi import package 
from yapapi.log import enable_default_logger, log_summary, log_event_repr 
from yapapi.package import vm 

from utils import (
    generate_schedule, 
    update_schedule,
    TEXT_COLOR_CYAN,
    TEXT_COLOR_DEFAULT,
    TEXT_COLOR_GREEN,
    TEXT_COLOR_RED,
    TEXT_COLOR_YELLOW,
)

base = pathlib.Path(__file__).resolve().parent
sys.path.append(str(base))

async def main():
    package = await vm.repo(
        image_hash="3edcb8953b432e6e653b49bd6323e0a93fd901db4c79ef3b13401aa2", #todo: update image hash
        min_mem_gib=0.5,
        min_storage_gib=2.0
    )

    async def worker_find_schedule(ctx: WorkContext, tasks):
        ctx.send_file("sa.py","/golem/work/sa.py")
        async for task in tasks:
            worker_num = task.data
            ctx.send_file(schedules[worker_num],f"/golem/work/schedule.txt")
            ctx.send_file(f"input/distances.txt","/golem/work/distances.txt")
            ctx.run("/bin/sh","-c",f"python3 sa.py --process {worker_num} > log.txt")
            ctx.download_file(f"/golem/work/schedule_{worker_num}.txt",f"output/schedules/schedule_{worker_num}.txt")
            ctx.download_file(f"/golem/work/cost_{worker_num}.txt",f"output/costs/cost_{worker_num}.txt")
            ctx.download_file(f"/golem/work/log.txt","output/log.txt")
            yield ctx.commit(timeout=timedelta(minutes=10))
            task.accept_result()
            
    schedules = ["input/s0.txt"]*NUM_PROVIDERS

    for wave in range(1,NUM_WAVES+1):
        async with Executor(
            package=package,
            max_workers=NUM_PROVIDERS,
            budget=BUDGET, #todo: set budget
            timeout=timedelta(minutes=10), #todo: set timeout
            driver="zksync",
            network="rinkeby",
            subnet_tag="devnet-beta.1",
            event_consumer=log_summary(log_event_repr), 
        ) as executor:

            tasks = [Task(data=num) for num in range(NUM_PROVIDERS)]
            async for task in executor.submit(worker_find_schedule,tasks):
                print(f"worker {task.data} completed its wave {wave}")
        update_schedule(NUM_PROVIDERS)
        schedules=["input/s0.txt"]*(NUM_PROVIDERS-2)
        schedules.append("input/s1.txt")
        schedules.append("input/s2.txt")

if __name__ == "__main__":
    
    enable_default_logger(log_file="log.txt")
    generate_schedule()
    SCHEDULE_SAVED = False
    loop = asyncio.get_event_loop()
    task = loop.create_task(main())

    try:
        loop.run_until_complete(task)
        S = generate_schedule_table()
        dfi.export(S,'schedule.png')
        SCHEDULE_SAVED = True
    except NoPaymentAccountError as e:
        print(
            f"{TEXT_COLOR_RED}",
            f"No payment account initialized for driver `{e.required_driver}` "
            f"and network `{e.required_network}`.\n\n"
            f"{TEXT_COLOR_DEFAULT}"
        )
    except KeyboardInterrupt:
        print(
            f"{TEXT_COLOR_YELLOW}"
            "Shutting down gracefully, please wait a short while "
            "or press Ctrl+C to exit immediately..."
            f"{TEXT_COLOR_DEFAULT}"
        )
        task.cancel()
        try:
            loop.run_until_complete(task)
            print(
                f"{TEXT_COLOR_YELLOW}Shutdown completed, thank you for waiting!{TEXT_COLOR_DEFAULT}"
            )
        except KeyboardInterrupt:
            pass
