BEGIN;
--
-- Create model CustomUser
--
CREATE TABLE "users_customuser" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "first_name" varchar(150) NOT NULL, "last_name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "user_type" varchar(10) NOT NULL);
CREATE TABLE "users_customuser_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "customuser_id" bigint NOT NULL REFERENCES "users_customuser" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "users_customuser_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "customuser_id" bigint NOT NULL REFERENCES "users_customuser" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX "users_customuser_groups_customuser_id_group_id_76b619e3_uniq" ON "users_customuser_groups" ("customuser_id", "group_id");
CREATE INDEX "users_customuser_groups_customuser_id_958147bf" ON "users_customuser_groups" ("customuser_id");
CREATE INDEX "users_customuser_groups_group_id_01390b14" ON "users_customuser_groups" ("group_id");
CREATE UNIQUE INDEX "users_customuser_user_permissions_customuser_id_permission_id_7a7debf6_uniq" ON "users_customuser_user_permissions" ("customuser_id", "permission_id");
CREATE INDEX "users_customuser_user_permissions_customuser_id_5771478b" ON "users_customuser_user_permissions" ("customuser_id");
CREATE INDEX "users_customuser_user_permissions_permission_id_baaa2f74" ON "users_customuser_user_permissions" ("permission_id");
COMMIT;
BEGIN;
--
-- Create model Profile
--
CREATE TABLE "users_profile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "certificate" varchar(100) NULL, "store_open_time" time NULL, "store_close_time" time NULL, "user_id" bigint NOT NULL UNIQUE REFERENCES "users_customuser" ("id") DEFERRABLE INITIALLY DEFERRED);
COMMIT;
BEGIN;
--
-- Alter field store_close_time on profile
--
CREATE TABLE "new__users_profile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "store_close_time" time NULL, "certificate" varchar(100) NULL, "store_open_time" time NULL, "user_id" bigint NOT NULL UNIQUE REFERENCES "users_customuser" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__users_profile" ("id", "certificate", "store_open_time", "user_id", "store_close_time") SELECT "id", "certificate", "store_open_time", "user_id", "store_close_time" FROM "users_profile";
DROP TABLE "users_profile";
ALTER TABLE "new__users_profile" RENAME TO "users_profile";
--
-- Alter field store_open_time on profile
--
CREATE TABLE "new__users_profile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "certificate" varchar(100) NULL, "store_close_time" time NULL, "user_id" bigint NOT NULL UNIQUE REFERENCES "users_customuser" ("id") DEFERRABLE INITIALLY DEFERRED, "store_open_time" time NULL);
INSERT INTO "new__users_profile" ("id", "certificate", "store_close_time", "user_id", "store_open_time") SELECT "id", "certificate", "store_close_time", "user_id", "store_open_time" FROM "users_profile";
DROP TABLE "users_profile";
ALTER TABLE "new__users_profile" RENAME TO "users_profile";
COMMIT;
BEGIN;
--
-- Add field bank_account_number to profile
--
CREATE TABLE "new__users_profile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "bank_account_number" varchar(20) NOT NULL, "certificate" varchar(100) NULL, "store_open_time" time NULL, "store_close_time" time NULL, "user_id" bigint NOT NULL UNIQUE REFERENCES "users_customuser" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__users_profile" ("id", "certificate", "store_open_time", "store_close_time", "user_id", "bank_account_number") SELECT "id", "certificate", "store_open_time", "store_close_time", "user_id", '' FROM "users_profile";
DROP TABLE "users_profile";
ALTER TABLE "new__users_profile" RENAME TO "users_profile";
--
-- Add field bank_routing_number to profile
--
CREATE TABLE "new__users_profile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "certificate" varchar(100) NULL, "store_open_time" time NULL, "store_close_time" time NULL, "user_id" bigint NOT NULL UNIQUE REFERENCES "users_customuser" ("id") DEFERRABLE INITIALLY DEFERRED, "bank_account_number" varchar(20) NOT NULL, "bank_routing_number" varchar(20) NOT NULL);
INSERT INTO "new__users_profile" ("id", "certificate", "store_open_time", "store_close_time", "user_id", "bank_account_number", "bank_routing_number") SELECT "id", "certificate", "store_open_time", "store_close_time", "user_id", "bank_account_number", '' FROM "users_profile";
DROP TABLE "users_profile";
ALTER TABLE "new__users_profile" RENAME TO "users_profile";
COMMIT;
BEGIN;
--
-- Add field is_approved to profile
--
CREATE TABLE "new__users_profile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "is_approved" bool NOT NULL, "certificate" varchar(100) NULL, "store_open_time" time NULL, "store_close_time" time NULL, "user_id" bigint NOT NULL UNIQUE REFERENCES "users_customuser" ("id") DEFERRABLE INITIALLY DEFERRED, "bank_account_number" varchar(20) NOT NULL, "bank_routing_number" varchar(20) NOT NULL);
INSERT INTO "new__users_profile" ("id", "certificate", "store_open_time", "store_close_time", "user_id", "bank_account_number", "bank_routing_number", "is_approved") SELECT "id", "certificate", "store_open_time", "store_close_time", "user_id", "bank_account_number", "bank_routing_number", 0 FROM "users_profile";
DROP TABLE "users_profile";
ALTER TABLE "new__users_profile" RENAME TO "users_profile";
COMMIT;
BEGIN;
--
-- Add field timezone to profile
--
CREATE TABLE "new__users_profile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "timezone" varchar(50) NOT NULL, "certificate" varchar(100) NULL, "store_open_time" time NULL, "store_close_time" time NULL, "user_id" bigint NOT NULL UNIQUE REFERENCES "users_customuser" ("id") DEFERRABLE INITIALLY DEFERRED, "bank_account_number" varchar(20) NOT NULL, "bank_routing_number" varchar(20) NOT NULL, "is_approved" bool NOT NULL);
INSERT INTO "new__users_profile" ("id", "certificate", "store_open_time", "store_close_time", "user_id", "bank_account_number", "bank_routing_number", "is_approved", "timezone") SELECT "id", "certificate", "store_open_time", "store_close_time", "user_id", "bank_account_number", "bank_routing_number", "is_approved", 'UTC' FROM "users_profile";
DROP TABLE "users_profile";
ALTER TABLE "new__users_profile" RENAME TO "users_profile";
COMMIT;
BEGIN;
--
-- Create model Meal
--
CREATE TABLE "orders_meal" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "description" text NOT NULL, "price" decimal NOT NULL, "image" varchar(100) NULL, "vendor_id" bigint NOT NULL REFERENCES "users_customuser" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "orders_meal_vendor_id_01688b25" ON "orders_meal" ("vendor_id");
COMMIT;
BEGIN;
--
-- Create model Order
--
CREATE TABLE "orders_order" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NOT NULL, "is_paid" bool NOT NULL, "customer_id" bigint NOT NULL REFERENCES "users_customuser" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model OrderItem
--
CREATE TABLE "orders_orderitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), "meal_id" bigint NOT NULL REFERENCES "orders_meal" ("id") DEFERRABLE INITIALLY DEFERRED, "order_id" bigint NOT NULL REFERENCES "orders_order" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "orders_order_customer_id_0b76f6a4" ON "orders_order" ("customer_id");
CREATE INDEX "orders_orderitem_meal_id_818d7533" ON "orders_orderitem" ("meal_id");
CREATE INDEX "orders_orderitem_order_id_fe61a34d" ON "orders_orderitem" ("order_id");
COMMIT;
BEGIN;
--
-- Add field status to order
--
CREATE TABLE "new__orders_order" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "status" varchar(10) NOT NULL, "created_at" datetime NOT NULL, "is_paid" bool NOT NULL, "customer_id" bigint NOT NULL REFERENCES "users_customuser" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__orders_order" ("id", "created_at", "is_paid", "customer_id", "status") SELECT "id", "created_at", "is_paid", "customer_id", 'DRAFT' FROM "orders_order";
DROP TABLE "orders_order";
ALTER TABLE "new__orders_order" RENAME TO "orders_order";
CREATE INDEX "orders_order_customer_id_0b76f6a4" ON "orders_order" ("customer_id");
--
-- Add field preferred_delivery_time to orderitem
--
ALTER TABLE "orders_orderitem" ADD COLUMN "preferred_delivery_time" datetime NULL;
--
-- Add field status to orderitem
--
CREATE TABLE "new__orders_orderitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), "meal_id" bigint NOT NULL REFERENCES "orders_meal" ("id") DEFERRABLE INITIALLY DEFERRED, "order_id" bigint NOT NULL REFERENCES "orders_order" ("id") DEFERRABLE INITIALLY DEFERRED, "preferred_delivery_time" datetime NULL, "status" varchar(20) NOT NULL);
INSERT INTO "new__orders_orderitem" ("id", "quantity", "meal_id", "order_id", "preferred_delivery_time", "status") SELECT "id", "quantity", "meal_id", "order_id", "preferred_delivery_time", 'CONFIRMED' FROM "orders_orderitem";
DROP TABLE "orders_orderitem";
ALTER TABLE "new__orders_orderitem" RENAME TO "orders_orderitem";
CREATE INDEX "orders_orderitem_meal_id_818d7533" ON "orders_orderitem" ("meal_id");
CREATE INDEX "orders_orderitem_order_id_fe61a34d" ON "orders_orderitem" ("order_id");
--
-- Create model Invoice
--
CREATE TABLE "orders_invoice" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "total_amount" decimal NOT NULL, "status" varchar(10) NOT NULL, "issued_at" datetime NOT NULL, "order_id" bigint NOT NULL UNIQUE REFERENCES "orders_order" ("id") DEFERRABLE INITIALLY DEFERRED);
COMMIT;
BEGIN;
--
-- Add field barcode_id to orderitem
--
CREATE TABLE "new__orders_orderitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "barcode_id" char(32) NOT NULL, "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), "meal_id" bigint NOT NULL REFERENCES "orders_meal" ("id") DEFERRABLE INITIALLY DEFERRED, "order_id" bigint NOT NULL REFERENCES "orders_order" ("id") DEFERRABLE INITIALLY DEFERRED, "preferred_delivery_time" datetime NULL, "status" varchar(20) NOT NULL);
INSERT INTO "new__orders_orderitem" ("id", "quantity", "meal_id", "order_id", "preferred_delivery_time", "status", "barcode_id") SELECT "id", "quantity", "meal_id", "order_id", "preferred_delivery_time", "status", '5eb97d136b9949aaac6a5cae462498e0' FROM "orders_orderitem";
DROP TABLE "orders_orderitem";
ALTER TABLE "new__orders_orderitem" RENAME TO "orders_orderitem";
CREATE INDEX "orders_orderitem_meal_id_818d7533" ON "orders_orderitem" ("meal_id");
CREATE INDEX "orders_orderitem_order_id_fe61a34d" ON "orders_orderitem" ("order_id");
COMMIT;
BEGIN;
--
-- Add field pickup_date to orderitem
--
CREATE TABLE "new__orders_orderitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "pickup_date" date NOT NULL, "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), "meal_id" bigint NOT NULL REFERENCES "orders_meal" ("id") DEFERRABLE INITIALLY DEFERRED, "order_id" bigint NOT NULL REFERENCES "orders_order" ("id") DEFERRABLE INITIALLY DEFERRED, "preferred_delivery_time" datetime NULL, "status" varchar(20) NOT NULL, "barcode_id" char(32) NOT NULL);
INSERT INTO "new__orders_orderitem" ("id", "quantity", "meal_id", "order_id", "preferred_delivery_time", "status", "barcode_id", "pickup_date") SELECT "id", "quantity", "meal_id", "order_id", "preferred_delivery_time", "status", "barcode_id", '2025-08-27' FROM "orders_orderitem";
DROP TABLE "orders_orderitem";
ALTER TABLE "new__orders_orderitem" RENAME TO "orders_orderitem";
CREATE INDEX "orders_orderitem_meal_id_818d7533" ON "orders_orderitem" ("meal_id");
CREATE INDEX "orders_orderitem_order_id_fe61a34d" ON "orders_orderitem" ("order_id");
--
-- Add field pickup_time to orderitem
--
CREATE TABLE "new__orders_orderitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), "meal_id" bigint NOT NULL REFERENCES "orders_meal" ("id") DEFERRABLE INITIALLY DEFERRED, "order_id" bigint NOT NULL REFERENCES "orders_order" ("id") DEFERRABLE INITIALLY DEFERRED, "preferred_delivery_time" datetime NULL, "status" varchar(20) NOT NULL, "barcode_id" char(32) NOT NULL, "pickup_date" date NOT NULL, "pickup_time" varchar(10) NOT NULL);
INSERT INTO "new__orders_orderitem" ("id", "quantity", "meal_id", "order_id", "preferred_delivery_time", "status", "barcode_id", "pickup_date", "pickup_time") SELECT "id", "quantity", "meal_id", "order_id", "preferred_delivery_time", "status", "barcode_id", "pickup_date", '12:00' FROM "orders_orderitem";
DROP TABLE "orders_orderitem";
ALTER TABLE "new__orders_orderitem" RENAME TO "orders_orderitem";
CREATE INDEX "orders_orderitem_meal_id_818d7533" ON "orders_orderitem" ("meal_id");
CREATE INDEX "orders_orderitem_order_id_fe61a34d" ON "orders_orderitem" ("order_id");
COMMIT;
BEGIN;
--
-- Alter field status on orderitem
--
-- (no-op)
COMMIT;
BEGIN;
--
-- Add field price to orderitem
--
CREATE TABLE "new__orders_orderitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "price" decimal NOT NULL, "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), "meal_id" bigint NOT NULL REFERENCES "orders_meal" ("id") DEFERRABLE INITIALLY DEFERRED, "order_id" bigint NOT NULL REFERENCES "orders_order" ("id") DEFERRABLE INITIALLY DEFERRED, "preferred_delivery_time" datetime NULL, "status" varchar(20) NOT NULL, "barcode_id" char(32) NOT NULL, "pickup_date" date NOT NULL, "pickup_time" varchar(10) NOT NULL);
INSERT INTO "new__orders_orderitem" ("id", "quantity", "meal_id", "order_id", "preferred_delivery_time", "status", "barcode_id", "pickup_date", "pickup_time", "price") SELECT "id", "quantity", "meal_id", "order_id", "preferred_delivery_time", "status", "barcode_id", "pickup_date", "pickup_time", '0' FROM "orders_orderitem";
DROP TABLE "orders_orderitem";
ALTER TABLE "new__orders_orderitem" RENAME TO "orders_orderitem";
CREATE INDEX "orders_orderitem_meal_id_818d7533" ON "orders_orderitem" ("meal_id");
CREATE INDEX "orders_orderitem_order_id_fe61a34d" ON "orders_orderitem" ("order_id");
COMMIT;
BEGIN;
--
-- Add field commission to order
--
CREATE TABLE "new__orders_order" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "commission" decimal NOT NULL, "created_at" datetime NOT NULL, "is_paid" bool NOT NULL, "customer_id" bigint NOT NULL REFERENCES "users_customuser" ("id") DEFERRABLE INITIALLY DEFERRED, "status" varchar(10) NOT NULL);
INSERT INTO "new__orders_order" ("id", "created_at", "is_paid", "customer_id", "status", "commission") SELECT "id", "created_at", "is_paid", "customer_id", "status", '0' FROM "orders_order";
DROP TABLE "orders_order";
ALTER TABLE "new__orders_order" RENAME TO "orders_order";
CREATE INDEX "orders_order_customer_id_0b76f6a4" ON "orders_order" ("customer_id");
COMMIT;
