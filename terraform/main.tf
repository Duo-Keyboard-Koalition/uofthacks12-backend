# Configure the Google Cloud Provider
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = "kataros"
  region  = "us-central1"
}

# Create an Autopilot GKE Cluster
resource "google_container_cluster" "my_gke_cluster" {
  name     = "uofthacks12-cluster"
  location = "us-central1"

  # Enable Autopilot
  enable_autopilot = true

  # Network Configuration
  networking_mode = "VPC_NATIVE"
  
  # Required for VPC-native clusters
  ip_allocation_policy {
    cluster_ipv4_cidr_block  = "/16"
    services_ipv4_cidr_block = "/22"
  }
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