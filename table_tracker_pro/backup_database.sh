#!/bin/bash
# Table Tracker Pro Database Backup Script

BACKUP_DIR="/home/h21s/table_tracker_pro/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="/home/h21s/table_tracker_pro/data/table_tracker.db"
EXPORT_FILE="/home/h21s/table_tracker_pro/data/customer_export.txt"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_DIR/table_tracker_$DATE.db"
    echo "✅ Database backed up: table_tracker_$DATE.db"
else
    echo "❌ Database file not found"
fi

# Backup export file
if [ -f "$EXPORT_FILE" ]; then
    cp "$EXPORT_FILE" "$BACKUP_DIR/customer_export_$DATE.txt"
    echo "✅ Export file backed up: customer_export_$DATE.txt"
fi

# Keep only last 10 backups
ls -t $BACKUP_DIR/table_tracker_*.db | tail -n +11 | xargs -r rm
ls -t $BACKUP_DIR/customer_export_*.txt | tail -n +11 | xargs -r rm

echo "🎯 Backup completed successfully!"
