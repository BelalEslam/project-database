-- First, backup the old data
CREATE TABLE IF NOT EXISTS old_product_backup AS SELECT * FROM product;
CREATE TABLE IF NOT EXISTS old_category_backup AS SELECT * FROM category;
CREATE TABLE IF NOT EXISTS old_user_backup AS SELECT * FROM user;

-- Migrate categories
INSERT INTO categories (name, description)
SELECT category_name, NULL FROM old_category_backup
WHERE category_name NOT IN (SELECT name FROM categories);

-- Migrate products
INSERT INTO products (name, description, price, stock, category_id, image_path)
SELECT 
    p.product_name,
    NULL, -- description was not in old table
    p.product_price,
    p.stock_quantity,
    c.id, -- new category id
    p.image_url
FROM old_product_backup p
JOIN categories c ON p.category_name = c.name;

-- Migrate users
INSERT INTO users (username, password, email, full_name, is_admin)
SELECT 
    username,
    password,
    email,
    full_name,
    is_admin
FROM old_user_backup;

-- Clean up backup tables (uncomment when ready to remove backups)
-- DROP TABLE IF EXISTS old_product_backup;
-- DROP TABLE IF EXISTS old_category_backup;
-- DROP TABLE IF EXISTS old_user_backup; 