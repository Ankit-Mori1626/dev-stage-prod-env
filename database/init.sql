-- Database Initialization Script for 3-Tier Multi-Cluster Project
-- Includes Tasks, Job Openings, Job Applications, and Service Inquiries

CREATE TABLE IF NOT EXISTS tasks (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(50) DEFAULT 'Pending',
  priority VARCHAR(20) DEFAULT 'Medium',
  environment VARCHAR(50) DEFAULT 'DEV',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_openings (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  department VARCHAR(100) NOT NULL,
  location VARCHAR(100) DEFAULT 'Remote / Hybrid',
  experience VARCHAR(50) NOT NULL,
  salary_range VARCHAR(100),
  description TEXT NOT NULL,
  skills TEXT[] NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_applications (
  id SERIAL PRIMARY KEY,
  job_id INTEGER REFERENCES job_openings(id) ON DELETE SET NULL,
  job_title VARCHAR(255) NOT NULL,
  candidate_name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  experience_years VARCHAR(50),
  portfolio_url VARCHAR(255),
  cover_note TEXT,
  status VARCHAR(50) DEFAULT 'Under Review',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS service_inquiries (
  id SERIAL PRIMARY KEY,
  client_name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  company_name VARCHAR(255),
  service_required VARCHAR(100) NOT NULL,
  budget VARCHAR(100),
  message TEXT NOT NULL,
  status VARCHAR(50) DEFAULT 'New Lead',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed initial records
INSERT INTO tasks (title, description, status, priority, environment) VALUES
  ('Kubeadm Multi-Cluster Provisioning', 'Setup Dev, Stage, and Prod clusters with containerd runtime and Calico CNI', 'Completed', 'High', 'DEV'),
  ('NGINX Ingress & MetalLB Setup', 'Configure Layer 2 VIPs with MetalLB and Path/Host routing with Ingress', 'In-Progress', 'High', 'STAGE'),
  ('Jenkins Multi-Branch Pipeline', 'Automate Git branch detection (dev/stage/prod) with Docker build & Kube deployment', 'Pending', 'Critical', 'PROD');

INSERT INTO job_openings (title, department, location, experience, salary_range, description, skills) VALUES
  ('Senior DevOps & Kubernetes Engineer', 'Cloud Infrastructure', 'Remote / Bengaluru', '4-7 Years', '$120k - $160k', 'Lead Kubeadm baremetal & EKS cluster deployments, Jenkins multi-branch pipelines, and MetalLB/ALB ingress configurations.', ARRAY['Kubernetes', 'Kubeadm', 'AWS ALB', 'Jenkins', 'Terraform', 'Docker']),
  ('Site Reliability Engineer (SRE)', 'Platform Operations', 'Remote / Hyderabad', '3-6 Years', '$110k - $145k', 'Build 99.999% SLA observability frameworks using Prometheus, Grafana, OpenTelemetry, and Chaos Engineering.', ARRAY['Prometheus', 'Grafana', 'Linux', 'Python', 'Go', 'Kubernetes']),
  ('Principal Cloud Solutions Architect', 'Enterprise Architecture', 'Hybrid / Noida', '8-12 Years', '$160k - $210k', 'Architect large-scale 3-tier enterprise workloads, hybrid-cloud networking, and zero-trust security postures.', ARRAY['AWS', 'Multi-Cluster K8s', 'Microservices', 'PostgreSQL', 'NetworkPolicy']),
  ('Full-Stack Python & React Developer', 'Product Engineering', 'Remote / Pune', '2-5 Years', '$90k - $130k', 'Develop responsive cloud telemetry dashboards, real-time analytics portals, and RESTful microservices.', ARRAY['Python', 'Streamlit', 'Node.js', 'React', 'PostgreSQL', 'Docker']);
