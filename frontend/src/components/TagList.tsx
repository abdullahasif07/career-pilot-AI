type TagListProps = {
  title: string;
  items: string[];
  emptyLabel?: string;
};

export default function TagList({ title, items, emptyLabel = "None listed" }: TagListProps) {
  return (
    <div className="tag-list">
      <h3 className="tag-list__title">{title}</h3>
      {items.length > 0 ? (
        <ul className="tag-list__items">
          {items.map((item) => (
            <li key={item} className="tag-list__item">
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">{emptyLabel}</p>
      )}
    </div>
  );
}
