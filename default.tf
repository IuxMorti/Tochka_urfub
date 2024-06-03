terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
      version = "0.119.0"
    }
  }
}

locals {
  folder_id = "b1gu9flm10gmav1nmpds"
  cloud_id = "b1gjirteuf0o5m3d3tkq"
}

provider "yandex" {
  service_account_key_file = "./authorized_key.json"
  cloud_id                 = local.cloud_id
  folder_id                = local.folder_id
  zone                     = "ru-central1-a"
}
