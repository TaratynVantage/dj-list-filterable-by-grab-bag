-- Let the app user create/drop Django's test database (`test_` + MYSQL_DATABASE).
GRANT ALL PRIVILEGES ON `test_app`.* TO 'app'@'%';
