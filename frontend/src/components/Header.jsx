import { Search, Bell } from "lucide-react";

function Header() {
  return (
    <header className="header">
      <div>
        <div className="breadcrumb">
          WORKSPACE / DASHBOARD
        </div>

        <h1>Sentiment Dashboard</h1>
      </div>

      <div className="header-right">
        <div className="search-box">
          <Search size={17} />

          <input
            type="text"
            placeholder="Search reviews..."
          />

          <span>⌘ K</span>
        </div>

        <button className="notification-btn">
          <Bell size={18} />
          <i></i>
        </button>

        <div className="profile">
          SR
        </div>
      </div>
    </header>
  );
}

export default Header;
