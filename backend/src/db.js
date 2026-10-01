const { Pool } = require('pg');

const useSSL = process.env.DB_SSL === 'true' || (process.env.DB_HOST && process.env.DB_HOST !== 'localhost');

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432', 10),
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'postgres',
  database: process.env.DB_NAME || 'threetierdb',
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 5000,
  ssl: useSSL ? { rejectUnauthorized: false } : false,
});

// Auto-initialize DB table if not exists with retry
async function initDB(retries = 5, delay = 3000) {
  for (let i = 0; i < retries; i++) {
    try {
      console.log(`[DB] Attempting database connection (Attempt ${i + 1}/${retries})...`);
      const client = await pool.connect();
      
      // Tasks table
      await client.query(`
        CREATE TABLE IF NOT EXISTS tasks (
          id SERIAL PRIMARY KEY,
          title VARCHAR(255) NOT NULL,
          description TEXT,
          status VARCHAR(50) DEFAULT 'Pending',
          priority VARCHAR(20) DEFAULT 'Medium',
          environment VARCHAR(50) DEFAULT 'DEV',
          created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
      `);

      // Job Openings table
      await client.query(`
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
      `);

      // Job Applications table
      await client.query(`
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
      `);

      // Service Inquiries table
      await client.query(`
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
      `);

      // Seed Job Openings if empty
      const jobsCount = await client.query('SELECT COUNT(*) FROM job_openings');
      if (parseInt(jobsCount.rows[0].count, 10) === 0) {
        await client.query(`
          INSERT INTO job_openings (title, department, location, experience, salary_range, description, skills) VALUES
          ('Senior DevOps & Kubernetes Engineer', 'Cloud Infrastructure', 'Remote / Bengaluru', '4-7 Years', '$120k - $160k', 'Lead Kubeadm baremetal & EKS cluster deployments, Jenkins multi-branch pipelines, and MetalLB/ALB ingress configurations.', ARRAY['Kubernetes', 'Kubeadm', 'AWS ALB', 'Jenkins', 'Terraform', 'Docker']),
          ('Site Reliability Engineer (SRE)', 'Platform Operations', 'Remote / Hyderabad', '3-6 Years', '$110k - $145k', 'Build 99.999% SLA observability frameworks using Prometheus, Grafana, OpenTelemetry, and Chaos Engineering.', ARRAY['Prometheus', 'Grafana', 'Linux', 'Python', 'Go', 'Kubernetes']),
          ('Principal Cloud Solutions Architect', 'Enterprise Architecture', 'Hybrid / Noida', '8-12 Years', '$160k - $210k', 'Architect large-scale 3-tier enterprise workloads, hybrid-cloud networking, and zero-trust security postures.', ARRAY['AWS', 'Multi-Cluster K8s', 'Microservices', 'PostgreSQL', 'NetworkPolicy']),
          ('Full-Stack Python & React Developer', 'Product Engineering', 'Remote / Pune', '2-5 Years', '$90k - $130k', 'Develop responsive cloud telemetry dashboards, real-time analytics portals, and RESTful microservices.', ARRAY['Python', 'Streamlit', 'Node.js', 'React', 'PostgreSQL', 'Docker']);
        `);
        console.log('[DB] Job openings seed data populated.');
      }

      // Seed Tasks if empty
      const res = await client.query('SELECT COUNT(*) FROM tasks');
      if (parseInt(res.rows[0].count, 10) === 0) {
        await client.query(`
          INSERT INTO tasks (title, description, status, priority, environment) VALUES
          ('Setup Kubeadm Clusters', 'Bootstrap Dev, Stage, and Prod Kubernetes clusters', 'Completed', 'High', 'DEV'),
          ('Configure MetalLB & Ingress', 'Setup LoadBalancer IP pool and NGINX Ingress Controller', 'In-Progress', 'High', 'STAGE'),
          ('Deploy Jenkins Multi-branch Pipeline', 'Automate CI/CD promotion across all environments', 'Pending', 'Medium', 'PROD');
        `);
      }

      client.release();
      console.log('[DB] Database connected and all corporate schemas verified.');
      return;
    } catch (err) {
      console.error(`[DB] Connection failed: ${err.message}`);
      if (i < retries - 1) {
        console.log(`[DB] Retrying in ${delay / 1000}s...`);
        await new Promise((res) => setTimeout(res, delay));
      } else {
        console.error('[DB] Maximum retries reached. Database might be initializing.');
      }
    }
  }
}

module.exports = { pool, initDB };
