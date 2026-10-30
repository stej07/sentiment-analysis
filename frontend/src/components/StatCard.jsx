function StatCard({
  title,
  value,
  change,
  description,
  icon: Icon,
  type = "default",
}) {
  return (
    <div className="stat-card">
      <div className="stat-heading">
        <span>{title}</span>

        <div className={`stat-icon ${type}`}>
          <Icon size={17} />
        </div>
      </div>

      <div className="stat-value">
        {value}
      </div>

      <div className="stat-footer">
        <strong>{change}</strong>
        <span>{description}</span>
      </div>
    </div>
  );
}

export default StatCard;
