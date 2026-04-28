# Screenshot Checklist for Submission

When submitting this prototype for the grant or portfolio, ensure you capture screenshots of the following scenarios:

- [ ] **1. Bot Initialization**: Show the terminal running `python src/main.py` without errors.
- [ ] **2. Help Menu**: Screenshot of the `/help` command output in Telegram.
- [ ] **3. Dry-Run Execution**: Run `/check_disk` while Dry-Run is ON. Show the simulated response.
- [ ] **4. Live Execution**: Toggle `/dry_run`, then run `/check_disk`. Show the actual OS output retrieved by the bot.
- [ ] **5. Safety Block**: Attempt to run a dangerous command (if testing via raw intent handler) or explain the denylist mechanism.
- [ ] **6. Audit Logs**: Show a snippet of the `execution_logs.jsonl` file verifying that the previous steps were recorded accurately.
