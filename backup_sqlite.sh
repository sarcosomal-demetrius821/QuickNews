#!/bin/bash

# QuickNews SQLite Database Backup Script
# This script creates timestamped backups of your SQLite database
# Usage: ./backup_sqlite.sh

set -e  # Exit on any error

# Configuration
PROJECT_DIR="/home/karanjot-singh/old_project_to_new_project/new_Django_News"
DB_FILE="$PROJECT_DIR/db.sqlite3"
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sqlite3"
KEEP_DAYS=30  # Keep backups for 30 days

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   QuickNews Database Backup Script    ${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${YELLOW}Creating backup directory...${NC}"
    mkdir -p "$BACKUP_DIR"
fi

# Check if database file exists
if [ ! -f "$DB_FILE" ]; then
    echo -e "${RED}❌ Error: Database file not found at $DB_FILE${NC}"
    exit 1
fi

# Get database size
DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
echo -e "${GREEN}📊 Database size: $DB_SIZE${NC}"

# Create backup
echo -e "${YELLOW}📦 Creating backup...${NC}"
cp "$DB_FILE" "$BACKUP_FILE"

if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup created successfully!${NC}"
    echo -e "${GREEN}   Location: $BACKUP_FILE${NC}"
    echo -e "${GREEN}   Size: $BACKUP_SIZE${NC}"
else
    echo -e "${RED}❌ Error: Backup failed!${NC}"
    exit 1
fi

# Compress backup
echo -e "${YELLOW}🗜️  Compressing backup...${NC}"
gzip "$BACKUP_FILE"
COMPRESSED_FILE="$BACKUP_FILE.gz"

if [ -f "$COMPRESSED_FILE" ]; then
    COMPRESSED_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup compressed!${NC}"
    echo -e "${GREEN}   Compressed size: $COMPRESSED_SIZE${NC}"
fi

# Clean up old backups
echo -e "${YELLOW}🧹 Cleaning up old backups (older than $KEEP_DAYS days)...${NC}"
find "$BACKUP_DIR" -name "db_backup_*.sqlite3.gz" -type f -mtime +$KEEP_DAYS -delete

REMAINING_BACKUPS=$(find "$BACKUP_DIR" -name "db_backup_*.sqlite3.gz" -type f | wc -l)
echo -e "${GREEN}✅ Cleanup complete. $REMAINING_BACKUPS backup(s) remaining.${NC}"

# List recent backups
echo -e "\n${GREEN}📋 Recent backups:${NC}"
ls -lh "$BACKUP_DIR" | grep "db_backup_" | tail -5

# Calculate total backup size
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo -e "\n${GREEN}💾 Total backup directory size: $TOTAL_SIZE${NC}"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}   Backup completed successfully! ✅   ${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Optional: Upload to cloud storage (uncomment if needed)
# echo -e "${YELLOW}☁️  Uploading to cloud storage...${NC}"
# # Example with AWS S3:
# # aws s3 cp "$COMPRESSED_FILE" s3://your-bucket/backups/
# # Example with Cloudflare R2:
# # aws s3 cp "$COMPRESSED_FILE" s3://your-r2-bucket/backups/ --endpoint-url=YOUR_R2_ENDPOINT

exit 0
