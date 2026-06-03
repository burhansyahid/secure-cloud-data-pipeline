terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 4.0.0"
    }
  }
}

# Tell Terraform to use the default profile from ~/.oci/config
provider "oci" {
  config_file_profile = "DEFAULT"
}

# 1. Provision the Object Storage Bucket (Data Lake)
resource "oci_objectstorage_bucket" "data_lake" {
  compartment_id = "ocid1.tenancy.oc1..aaaaaaaan5nl4ui7tnp43jbbqfcou3sn4rw27sehzoalkmzgflu4ly5r77dq"
  name           = "portfolio_data_lake"
  namespace      = "axhrcbgwo7cd"
  access_type    = "NoPublicAccess"
}

# 2. Provision the Autonomous Data Warehouse
resource "oci_database_autonomous_database" "portfolio_adw" {
  compartment_id           = "ocid1.tenancy.oc1..aaaaaaaan5nl4ui7tnp43jbbqfcou3sn4rw27sehzoalkmzgflu4ly5r77dq"
  db_name                  = "portfoliodb"
  display_name             = "portfolio_lakehouse"
  db_workload              = "DW"
  is_free_tier             = true
  admin_password           = "PortfolioLakehouse_2026!"
  cpu_core_count           = 1
  data_storage_size_in_tbs = 1
}
