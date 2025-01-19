terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }

  backend "gcs" {
    bucket = "kataros-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# GKE Cluster
resource "google_container_cluster" "my_gke_cluster" {
  name     = var.cluster_name
  location = var.region

  enable_autopilot = true
  networking_mode  = "VPC_NATIVE"
  
  ip_allocation_policy {
    cluster_ipv4_cidr_block  = "/16"
    services_ipv4_cidr_block = "/22"
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
}

# Reference GitHub Actions Workload Identity
module "github_actions" {
  source = "./modules/github-actions"
  
  project_id = var.project_id
  pool_id    = google_iam_workload_identity_pool.github_pool.id
}

# Outputs
output "cluster_endpoint" {
  value = google_container_cluster.my_gke_cluster.endpoint
}

output "cluster_name" {
  value = google_container_cluster.my_gke_cluster.name
}

output "location" {
  value = google_container_cluster.my_gke_cluster.location
}

output "workload_identity_pool" {
  value = google_iam_workload_identity_pool.github_pool.name
}