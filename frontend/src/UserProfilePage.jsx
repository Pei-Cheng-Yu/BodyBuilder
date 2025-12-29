import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api";
import "./UserProfilePage.css";

function TagInput({ label, value, onChange, placeholder }) {
  const [draft, setDraft] = useState("");

  const addTag = () => {
    const t = draft.trim();
    if (!t) return;
    if (value.includes(t)) {
      setDraft("");
      return;
    }
    onChange([...value, t]);
    setDraft("");
  };

  const removeTag = (tag) => {
    onChange(value.filter((x) => x !== tag));
  };

  return (
    <div className="field">
      <label className="label">{label}</label>

      <div className="tagBox">
        {value.map((tag) => (
          <span key={tag} className="tag">
            {tag}
            <button
              type="button"
              className="tagRemove"
              onClick={() => removeTag(tag)}
              aria-label={`remove ${tag}`}
            >
              ×
            </button>
          </span>
        ))}
      </div>

      <div className="tagInputRow">
        <input
          className="input"
          value={draft}
          placeholder={placeholder}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              addTag();
            }
          }}
        />
        <button type="button" className="btn" onClick={addTag}>
          Add
        </button>
      </div>

      <div className="hint">Type and press Enter to add.</div>
    </div>
  );
}

export default function UserProfilePage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");

  const [form, setForm] = useState({
    gender: "",
    age: "",
    workout_frequency: 3,
    user_goal: "",
    injuries: [],
    load: "",
    training_location: "gym",
    available_equipment: [],
    avoid_equipment: [],
  });

  const navigate = useNavigate();

  // Check authentication using /auth/me API
  useEffect(() => {
    const checkAuthentication = async () => {
      setErr("");
      setLoading(true);
      try {
        // Check if the user is logged in by calling /auth/me
        await api.get("/auth/me");

        // Fetch the profile if authenticated
        const profileRes = await api.get("/profile/me");
        const p = profileRes.data;

        // Set the profile data to the form state
        setForm({
          gender: p.gender ?? "",
          age: p.age ?? "",
          workout_frequency: p.workout_frequency ?? 3,
          user_goal: p.user_goal ?? "",
          injuries: Array.isArray(p.injuries) ? p.injuries : [],
          load: p.load ?? "",
          training_location: p.training_location ?? "gym",
          available_equipment: Array.isArray(p.available_equipment)
            ? p.available_equipment
            : [],
          avoid_equipment: Array.isArray(p.avoid_equipment)
            ? p.avoid_equipment
            : [],
        });
      } catch (e) {
        setErr(e?.response?.data?.detail || "You are not logged in.");
        navigate("/login", { replace: true });
      } finally {
        setLoading(false);
      }
    };

    checkAuthentication();
  }, [navigate]);

  const setField = (k, v) => setForm((prev) => ({ ...prev, [k]: v }));

  const onSave = async () => {
    setErr("");
    setSaving(true);
    try {
      const payload = {
        gender: form.gender || null,
        age: form.age === "" ? null : Number(form.age),
        workout_frequency: Number(form.workout_frequency),
        user_goal: form.user_goal || null,
        injuries: form.injuries,
        load: form.load === "" ? null : Number(form.load),
        training_location: form.training_location,
        available_equipment: form.available_equipment,
        avoid_equipment: form.avoid_equipment,
      };

      const res = await api.put("/profile/me", payload);
      const p = res.data;

      // sync normalized response back
      setForm({
        gender: p.gender ?? "",
        age: p.age ?? "",
        workout_frequency: p.workout_frequency ?? 3,
        user_goal: p.user_goal ?? "",
        injuries: Array.isArray(p.injuries) ? p.injuries : [],
        load: p.load ?? "",
        training_location: p.training_location ?? "gym",
        available_equipment: Array.isArray(p.available_equipment)
          ? p.available_equipment
          : [],
        avoid_equipment: Array.isArray(p.avoid_equipment)
          ? p.avoid_equipment
          : [],
      });

      alert("✅ Profile saved");
    } catch (e) {
      setErr(e?.response?.data?.detail || "Failed to save profile");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="muted">Loading...</div>;
  if (err) return <div className="error">{err}</div>;

  return (
    <div className="profileWrap">
      <div className="card">
        <div className="headerRow">
          <h2 className="title">User Profile</h2>
          <button
            className="btn primary"
            disabled={loading || saving}
            onClick={onSave}
          >
            {saving ? "Saving..." : "Save"}
          </button>
        </div>

        <form className="grid" onSubmit={(e) => e.preventDefault()}>
          <div className="field">
            <label className="label">Gender</label>
            <select
              className="input"
              value={form.gender}
              onChange={(e) => setField("gender", e.target.value)}
            >
              <option value="">(not set)</option>
              <option value="male">male</option>
              <option value="female">female</option>
              <option value="other">other</option>
            </select>
          </div>

          <div className="field">
            <label className="label">Age</label>
            <input
              className="input"
              type="number"
              value={form.age}
              placeholder="e.g. 21"
              onChange={(e) => setField("age", e.target.value)}
              min={0}
            />
          </div>

          <div className="field">
            <label className="label">Workout frequency (days/week)</label>
            <input
              className="input"
              type="number"
              value={form.workout_frequency}
              onChange={(e) => setField("workout_frequency", e.target.value)}
              min={0}
              max={14}
            />
          </div>

          <div className="field full">
            <label className="label">User goal</label>
            <input
              className="input"
              value={form.user_goal}
              placeholder="e.g. muscle gain / fat loss / strength"
              onChange={(e) => setField("user_goal", e.target.value)}
            />
          </div>

          <TagInput
            label="Injuries"
            value={form.injuries}
            onChange={(v) => setField("injuries", v)}
            placeholder="e.g. knee pain"
          />

          <div className="field">
            <label className="label">Training location</label>
            <select
              className="input"
              value={form.training_location}
              onChange={(e) => setField("training_location", e.target.value)}
            >
              <option value="gym">gym</option>
              <option value="home">home</option>
              <option value="both">both</option>
            </select>
          </div>

          <TagInput
            label="Available equipment"
            value={form.available_equipment}
            onChange={(v) => setField("available_equipment", v)}
            placeholder="e.g. dumbbells"
          />

          <TagInput
            label="Avoid equipment"
            value={form.avoid_equipment}
            onChange={(v) => setField("avoid_equipment", v)}
            placeholder="e.g. barbell"
          />
        </form>
      </div>
    </div>
  );
}
