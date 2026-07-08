# War Zone — Vercel Deployment

## Deploy

1. Create a new Vercel project.
2. Upload/import this folder.
3. Set the environment variables below in Vercel Project Settings.
4. Deploy.

## Required / recommended environment variables

```txt
REGISTRATION_ADMIN_PASSWORD=BeshooWarZone
REGISTRATION_DATA_DIR=/tmp/registration_data
WARZONE_DATA_FILE=/tmp/warzone_data.json
```

For Google Drive image storage, also add:

```txt
GOOGLE_DRIVE_FOLDER_ID=<your_google_drive_folder_id>
GOOGLE_SERVICE_ACCOUNT_JSON_B64=<base64_service_account_json>
GOOGLE_DRIVE_DELETE_ON_TEAM_DELETE=true
```

## Important Vercel note

Vercel serverless storage is ephemeral. Files/data written to `/tmp` can disappear between cold starts/deployments. For production registrations, use Google Drive for uploaded files and consider moving JSON data to a real database or external storage.

## Included Vercel changes

- Added `vercel.json`
- Changed `warzone_data.json` default path to `/tmp/warzone_data.json`
- Changed registration submit URL from the old Railway absolute URL to `/api/register-team-json`

## Persistent storage across code changes

This version stores runtime changes in Google Drive when these variables are set:

```txt
GOOGLE_DRIVE_FOLDER_ID=<your_google_drive_folder_id>
GOOGLE_SERVICE_ACCOUNT_JSON_B64=<base64_service_account_json>
WARZONE_DRIVE_DATA_PREFIX=warzone_data
```

The app will keep these files in the selected Drive folder:

```txt
warzone_data_warzone_main.json       # tournaments, matches, results, draws, admin settings
warzone_data_registrations.json      # registered teams and players
warzone_data_whatsapp_groups.json    # WhatsApp group assignments
file_...                             # uploaded player photos/cards
```

If the Drive variables are missing, the app falls back to `/tmp`, which is temporary on Vercel.
