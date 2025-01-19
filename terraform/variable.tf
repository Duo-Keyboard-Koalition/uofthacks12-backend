variable "project_id" {
  description = "The project ID to deploy to"
  type        = string
  default     = "kataros"
}

variable "region" {
  description = "The region to deploy to"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "The name for the GKE cluster"
  type        = string
  default     = "uofthacks12-cluster"
}


variable "service_account_id" {
  description = "The ID of the service account for workload identity"
  type        = string
  default     = "github-actions-sa"
}