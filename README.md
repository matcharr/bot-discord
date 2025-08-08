# Discord Moderation Bot

A comprehensive Discord bot with moderation tools, anti-raid protection, and server management features.

## Quick Start

1. Install dependencies: `pip install discord.py`
2. Create a "logs" channel in your Discord server
3. Update `channel_id` in `reporting.py` with your report channel ID
4. Load all cogs in your main bot file

## Features & Commands

### 🛡️ Anti-Raid Protection
Automatically detects and kicks spammers (10+ messages triggers kick, 10-second cooldown per message).

### ⚖️ Moderation Commands
- `/warn @user reason` - Issue warnings (stored in warnings.json)
- `/warnings @user` - View user warnings
- `/kick @user reason` - Kick user
- `/ban @user reason` - Ban user  
- `/unban user#1234` - Unban user
- `/mute @user reason` - Mute user (creates Muted role)
- `/tempban @user 1h reason` - Temporary ban (m/h/d)
- `/tempmute @user 30m reason` - Temporary mute
- `/purge 10 @user` - Delete messages (optional user filter)

### 🔧 Role Management
- `/create_role name color` - Create new role
- `/delete_role @role` - Delete role
- `/add_role @user @role` - Assign role
- `/remove_role @user @role` - Remove role

### 📊 Logging & Monitoring
- **Auto-logs**: Message deletions, member joins/leaves to #logs channel
- **Invite tracking**: Monitors invite creation/deletion and usage
- **Report system**: `/report @user reason` sends reports to moderators

## Required Bot Permissions

```
✅ Send Messages          ✅ Manage Messages
✅ Kick Members           ✅ Ban Members  
✅ Manage Roles           ✅ View Audit Log
✅ Embed Links            ✅ Manage Guild
```

## Setup Checklist

1. Create `#logs` channel for event logging
2. Create report channel and update ID in `reporting.py` line 16
3. Ensure bot role is above roles it needs to manage
4. Test with `/warn @user test` to verify warnings.json creation

## File Structure
```
project/cogs/
├── anti_raid.py      # Spam detection & auto-kick
├── moderation.py     # Warning/kick/ban/mute commands  
├── logging_system.py # Event logging to #logs
├── role_management.py # Role creation & assignment
├── invite_management.py # Invite tracking
└── reporting.py      # User reporting system
```

## Loading Cogs
```python
# In your main bot file
cogs = ['anti_raid', 'moderation', 'logging_system', 
        'role_management', 'invite_management', 'reporting']

for cog in cogs:
    await bot.load_extension(f'cogs.{cog}')
```