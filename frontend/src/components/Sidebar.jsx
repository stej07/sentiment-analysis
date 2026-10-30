import {
  LayoutDashboard,
  Globe,
  MessageSquareText,
  BarChart3,
  Brain,
  Settings,
  Activity,
} from "lucide-react";

function Sidebar({ activePage, setActivePage }) {
  const menuItems = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "Web Scraper", icon: Globe },
    { name: "Sentiment Analysis", icon: MessageSquareText },
    { name: "Analytics", icon: BarChart3 },
    { name: "Model Performance", icon: Brain },
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-logo">
          <Activity size={21} />
        </div>

        <div>
          <h2>Sentiment<span>AI</span></h2>
          <p>ML ANALYTICS</p>
        </div>
      </div>

      <div className="menu-title">MAIN MENU</div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.name}
              className={`nav-item ${
                activePage === item.name ? "active" : ""
              }`}
              onClick={() => setActivePage(item.name)}
            >
              <Icon size={18} />
              <span>{item.name}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <button className="nav-item">
          <Settings size={18} />
          <span>Settings</span>
        </button>

        <div className="system-card">
          <div className="online-dot"></div>

          <div>
            <strong>System Online</strong>
            <small>ML engine ready</small>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
