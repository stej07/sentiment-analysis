import {
  Database,
  Smile,
  Meh,
  Frown,
  ArrowUpRight,
  Activity,
} from "lucide-react";

function Dashboard() {
  return (
    <div className="dashboard">

      <section className="welcome-card">
        <div>
          <div className="live-status">
            <span></span>
            LIVE ANALYSIS
          </div>

          <h2>
            Understand what people
            <br />
            <strong>really think.</strong>
          </h2>

          <p>
            Scrape reviews from the web, analyze their sentiment,
            and turn raw opinions into useful insights.
          </p>

          <button className="primary-button">
            Start Analysis
            <ArrowUpRight size={17} />
          </button>
        </div>

        <div className="welcome-visual">
          <div className="visual-circle"></div>

          <div className="engine-card">
            <Activity size={23} />
            <div>
              <b>ML Engine</b>
              <small>Ready to analyze</small>
            </div>
            <span className="online"></span>
          </div>
        </div>
      </section>

      <section className="stats-grid">

        <div className="stat-card">
          <div className="stat-title">
            <span>Total Reviews</span>
            <Database size={18} />
          </div>
          <h3>12,486</h3>
          <p className="up">+18.4% <span>this month</span></p>
        </div>

        <div className="stat-card">
          <div className="stat-title">
            <span>Positive</span>
            <Smile size={18} />
          </div>
          <h3>72.4%</h3>
          <p className="up">+6.2% <span>from last analysis</span></p>
        </div>

        <div className="stat-card">
          <div className="stat-title">
            <span>Neutral</span>
            <Meh size={18} />
          </div>
          <h3>18.2%</h3>
          <p className="normal">-1.8% <span>from last analysis</span></p>
        </div>

        <div className="stat-card">
          <div className="stat-title">
            <span>Negative</span>
            <Frown size={18} />
          </div>
          <h3>9.4%</h3>
          <p className="up">-4.4% <span>from last analysis</span></p>
        </div>

      </section>

      <section className="dashboard-grid">

        <div className="dashboard-panel">

          <div className="panel-title">
            <div>
              <small>SENTIMENT OVERVIEW</small>
              <h3>Sentiment trend</h3>
            </div>

            <select>
              <option>Last 30 days</option>
              <option>Last 7 days</option>
              <option>Last 90 days</option>
            </select>
          </div>

          <div className="fake-chart">

            <div className="chart-lines">
              <span></span>
              <span></span>
              <span></span>
              <span></span>
            </div>

            <div className="chart-bars">
              <i style={{ height: "35%" }}></i>
              <i style={{ height: "45%" }}></i>
              <i style={{ height: "40%" }}></i>
              <i style={{ height: "55%" }}></i>
              <i style={{ height: "50%" }}></i>
              <i style={{ height: "65%" }}></i>
              <i style={{ height: "58%" }}></i>
              <i style={{ height: "75%" }}></i>
              <i style={{ height: "70%" }}></i>
              <i style={{ height: "85%" }}></i>
              <i style={{ height: "78%" }}></i>
              <i style={{ height: "92%" }}></i>
            </div>

            <div className="chart-labels">
              <span>Aug 01</span>
              <span>Aug 07</span>
              <span>Aug 14</span>
              <span>Aug 21</span>
              <span>Aug 30</span>
            </div>

          </div>

        </div>

        <div className="dashboard-panel distribution-panel">

          <div className="panel-title">
            <div>
              <small>CLASSIFICATION</small>
              <h3>Distribution</h3>
            </div>
          </div>

          <div className="sentiment-ring">
            <div>
              <strong>72.4%</strong>
              <span>Positive</span>
            </div>
          </div>

          <div className="legend-row">
            <span className="dot positive-dot"></span>
            <span>Positive</span>
            <b>72.4%</b>
          </div>

          <div className="legend-row">
            <span className="dot neutral-dot"></span>
            <span>Neutral</span>
            <b>18.2%</b>
          </div>

          <div className="legend-row">
            <span className="dot negative-dot"></span>
            <span>Negative</span>
            <b>9.4%</b>
          </div>

        </div>

      </section>

      <section className="dashboard-panel reviews-panel">

        <div className="panel-title">
          <div>
            <small>LATEST DATA</small>
            <h3>Recent reviews</h3>
          </div>

          <button className="view-button">
            View all
            <ArrowUpRight size={14} />
          </button>
        </div>

        <div className="review-item">
          <div className="review-icon positive-review">
            <Smile size={17} />
          </div>

          <div className="review-text">
            <b>Excellent product and amazing experience</b>
            <span>Collected from web • 2 minutes ago</span>
          </div>

          <label className="positive-label">Positive</label>
          <strong>96%</strong>
        </div>

        <div className="review-item">
          <div className="review-icon neutral-review">
            <Meh size={17} />
          </div>

          <div className="review-text">
            <b>It works well, but there is room for improvement</b>
            <span>Collected from web • 8 minutes ago</span>
          </div>

          <label className="neutral-label">Neutral</label>
          <strong>68%</strong>
        </div>

        <div className="review-item">
          <div className="review-icon negative-review">
            <Frown size={17} />
          </div>

          <div className="review-text">
            <b>Very disappointing experience with this service</b>
            <span>Collected from web • 14 minutes ago</span>
          </div>

          <label className="negative-label">Negative</label>
          <strong>91%</strong>
        </div>

      </section>

    </div>
  );
}

export default Dashboard;
