#/bin/bash
# usage details: ./postgres_restore_post.sh almanet xepa4ep
DB_NAME=$1
DB_USER=$2
echo $DB_NAME
for tbl in `psql -qAt -c "select tablename from pg_tables where schemaname = 'public';" -d ${DB_NAME}`
do
psql -d $DB_NAME << EOF
    alter table $tbl owner to $DB_USER
EOF
done

echo "tables altered"

for tbl in `psql -qAt -c "select sequence_name from information_schema.sequences where sequence_schema = 'public';" -d ${DB_NAME}`
do
psql -d $DB_NAME << EOF
    alter table $tbl owner to $DB_USER
EOF
done

echo "seq altered"

for tbl in `psql -qAt -c "select table_name from information_schema.views where table_schema = 'public';" -d ${DB_NAME}`
do
psql -d $DB_NAME << EOF
    alter table $tbl owner to $DB_USER
EOF
done

echo "views altered"