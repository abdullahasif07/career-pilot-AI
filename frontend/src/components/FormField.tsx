type FormFieldProps = {
  id: string;
  label: string;
  hint?: string;
  type?: "text" | "url" | "textarea";
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  rows?: number;
};

export default function FormField({
  id,
  label,
  hint,
  type = "text",
  value,
  onChange,
  placeholder,
  rows = 4,
}: FormFieldProps) {
  return (
    <div className="form-field">
      <label className="form-field__label" htmlFor={id}>
        {label}
      </label>
      {hint && <p className="form-field__hint">{hint}</p>}
      {type === "textarea" ? (
        <textarea
          id={id}
          className="form-field__input form-field__input--textarea"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          rows={rows}
        />
      ) : (
        <input
          id={id}
          type={type}
          className="form-field__input"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
        />
      )}
    </div>
  );
}
