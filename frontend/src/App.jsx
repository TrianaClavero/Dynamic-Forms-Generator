import { useMemo, useState } from 'react';
import { jsPDF } from 'jspdf';

const fieldTypes = [
    { value: 'string', label: 'Texto' },
    { value: 'number', label: 'Número' },
    { value: 'boolean', label: 'Checkbox' },
    { value: 'date', label: 'Fecha' },
    { value: 'email', label: 'Email' },
];

const typeToJsonType = {
    string: 'string',
    number: 'number',
    boolean: 'boolean',
    date: 'string',
    email: 'string',
};

const typeToFormat = {
    date: 'date',
    email: 'email',
};

function App() {
    const [title, setTitle] = useState('Formulario de prueba');
    const [description, setDescription] = useState('Este es un formulario de prueba');
    const [fields, setFields] = useState([
        { id: 1, label: 'Nombre', type: 'string', required: true, maxLength: 50, helpText: '' },
        { id: 2, label: 'Edad', type: 'number', required: true, maxLength: 3, helpText: '' },
    ]);
    const [nextId, setNextId] = useState(3);
    const [status, setStatus] = useState('');
    const [showPreview, setShowPreview] = useState(false);
    const [selectedFieldId, setSelectedFieldId] = useState(1);

    const schema = useMemo(() => {
        const properties = {};
        const required = [];

        fields.forEach((field) => {
            properties[field.id] = {
                title: field.label,
                type: typeToJsonType[field.type] || 'string',
            };
            const format = typeToFormat[field.type];
            if (format) properties[field.id].format = format;
            if (field.type === 'string' && field.maxLength) {
                properties[field.id].maxLength = field.maxLength;
            }
            if (field.type === 'number' && field.maxLength) {
                properties[field.id].maximum = field.maxLength;
            }
            if (field.helpText) {
                properties[field.id].description = field.helpText;
            }
            if (field.required) required.push(field.id);
        });

        return {
            type: 'object',
            title,
            description,
            properties,
            required,
            additionalProperties: false,
        };
    }, [title, description, fields]);

    const onSubmit = async () => {
        setStatus('Enviando formulario...');
        try {
            const resp = await fetch('http://localhost:8000/forms/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title,
                    description,
                    definition: schema,
                }),
            });
            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.detail || 'Error al crear formulario');
            }
            const data = await resp.json();
            setStatus(`Formulario creado con id ${data.id}`);
        } catch (e) {
            setStatus(`Error: ${e.message}`);
        }
    };

    const addField = () => {
        const newField = { id: nextId, label: `Campo ${nextId}`, type: 'string', required: false, maxLength: 100, helpText: '' };
        setFields((prev) => [...prev, newField]);
        setSelectedFieldId(newField.id);
        setNextId((x) => x + 1);
    };

    const updateField = (id, partial) => {
        setFields((prev) => prev.map((f) => (f.id === id ? { ...f, ...partial } : f)));
    };

    const moveField = (id, direction) => {
        setFields((prev) => {
            const index = prev.findIndex((f) => f.id === id);
            if (index < 0) return prev;
            const to = index + direction;
            if (to < 0 || to >= prev.length) return prev;
            const next = [...prev];
            const temp = next[to];
            next[to] = next[index];
            next[index] = temp;
            return next;
        });
    };

    const deleteField = (id) => {
        setFields((prev) => prev.filter((f) => f.id !== id));
        if (selectedFieldId === id && fields.length > 1) {
            const nextField = fields.find((f) => f.id !== id);
            setSelectedFieldId(nextField?.id ?? null);
        }
    };

    const selectedField = fields.find((f) => f.id === selectedFieldId) ?? fields[0];

    return (
        <div className="main-container">
            {/* Barra de acciones */}
            <div className="sidebar">
                <div className="sidebar-navbar">
                    <button className="secondary" onClick={() => setShowPreview((v) => !v)}>
                        {showPreview ? 'Ocultar previsualización' : 'Previsualizar'}
                    </button>
                    <button className="secondary" onClick={() => {
                        const doc = new jsPDF();
                        doc.text(`Formulario: ${title}`, 10, 10);
                        doc.text(`Descripción: ${description}`, 10, 20);
                        doc.text(JSON.stringify(schema, null, 2), 10, 30);
                        const pdfBlob = doc.output('blob');
                        const url = URL.createObjectURL(pdfBlob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `${title.replace(/\s+/g, '_')}.pdf`;
                        a.click();
                        URL.revokeObjectURL(url);
                    }}>
                        Descargar PDF
                    </button>
                    <button className="primary" onClick={onSubmit}>Guardar</button>
                </div>
                {status && <p style={{ marginTop: 8 }}>{status}</p>}
            </div>
                <h1>Constructor de Formulario Dinámico</h1>
                <div className="section">
                    <label>Título</label>
                    <input value={title} onChange={(e) => setTitle(e.target.value)} />
                </div>
                <div className="section">
                    <label>Descripción</label>
                    <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={2} />
                </div>
            <div className="container">
            {/* Editor de campos */}
            <div style={{ flex: 2, display: 'flex', gap: 12, border: '1px solid #e2e8f0', borderRadius: 10, padding: 12, background: '#fff' }}>

                <div className="page-layout">
                    
                        <div className="field-list">
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            </div>
                            {fields.length === 0 && <small>No hay campos. Agrega uno.</small>}
                            {fields.map((field, i) => (
                                <div
                                    key={field.id}
                                    className="field-card"
                                    style={{ borderColor: selectedFieldId === field.id ? '#2563eb' : '#e2e8f0', cursor: 'pointer' }}
                                    onClick={() => setSelectedFieldId(field.id)}
                                >
                                    <div style={{ width: '100%' }}>
                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 120px 120px', gap: 8 }}>
                                            <input
                                                value={field.label}
                                                onChange={(e) => updateField(field.id, { label: e.target.value })}
                                                placeholder="Etiqueta"
                                            />
                                        </div>
                                        <small>Orden: {i + 1}</small>
                                    </div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                                        <button className="secondary" onClick={(e) => { e.stopPropagation(); moveField(field.id, -1); }} disabled={i === 0}>↑</button>
                                        <button className="secondary" onClick={(e) => { e.stopPropagation(); moveField(field.id, 1); }} disabled={i === fields.length - 1}>↓</button>
                                        <button className="danger" onClick={(e) => { e.stopPropagation(); deleteField(field.id); }}>Eliminar</button>
                                    </div>
                                </div>
                            ))}
                            <div style={{ marginTop: 10 }}>
                                <button onClick={addField}>+ Agregar campo</button>
                            </div>
                        </div>

                        <div className="preview-section">
                            {showPreview ? (
                                <>
                                    <h3>Vista previa</h3>
                                    <div className="preview-card">
                                        <h4>{title}</h4>
                                        <p>{description}</p>
                                        {fields.length === 0 && <p style={{ color: '#6b7280' }}>No hay campos para mostrar.</p>}
                                        {fields.map((field) => (
                                            <div key={`preview-${field.id}`} style={{ marginBottom: 10 }}>
                                                <label style={{ display: 'block', marginBottom: 4 }}>{field.label} {field.required ? '*' : ''}</label>
                                                {field.type === 'boolean' ? (
                                                    <input type="checkbox" />
                                                ) : field.type === 'date' ? (
                                                    <input type="date" />
                                                ) : field.type === 'email' ? (
                                                    <input type="email" placeholder={field.label} />
                                                ) : (
                                                    <input type={field.type === 'number' ? 'number' : 'text'} placeholder={field.label} />
                                                )}
                                                {field.helpText && <small style={{ color: '#6b7280', marginTop: 4, display: 'block' }}>{field.helpText}</small>}
                                            </div>
                                        ))}
                                    </div>
                                </>
                            ) : (
                                <>
                                    <h3>JSON Schema generado</h3>
                                    <pre>{JSON.stringify(schema, null, 2)}</pre>
                                </>
                            )}
                        </div>
                  

                </div>
            </div>
            {/* Configuración de campo seleccionado */}
            <div style={{ flex: 1, border: '1px solid #e2e8f0', borderRadius: 10, padding: 12, background: '#fff' }}>
                <h3>Configuración de campo</h3>
                {!selectedField ? (
                    <p>Selecciona un campo para editar.</p>
                ) : (
                    <>
                        <div style={{ marginBottom: 10 }}>
                            <label>Nombre</label>
                            <input
                                value={selectedField.label}
                                onChange={(e) => updateField(selectedField.id, { label: e.target.value })}
                            />
                        </div>
                        <div style={{ marginBottom: 10 }}>
                            <label>Tipo</label>
                            <select
                                value={selectedField.type}
                                onChange={(e) => updateField(selectedField.id, { type: e.target.value })}
                            >
                                {fieldTypes.map((item) => (
                                    <option key={item.value} value={item.value}>{item.label}</option>
                                ))}
                            </select>
                        </div>
                        <div style={{ marginBottom: 10 }}>
                            <label style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                                <input
                                    type="checkbox"
                                    checked={selectedField.required}
                                    onChange={(e) => updateField(selectedField.id, { required: e.target.checked })}
                                />
                                Obligatorio
                            </label>
                        </div>
                        {(selectedField.type === 'string' || selectedField.type === 'number') && (
                            <div style={{ marginBottom: 10 }}>
                                <label>{selectedField.type === 'string' ? 'Máximo caracteres' : 'Valor máximo'}</label>
                                <input
                                    type="number"
                                    value={selectedField.maxLength ?? ''}
                                    onChange={(e) => updateField(selectedField.id, { maxLength: e.target.value ? Number(e.target.value) : undefined })}
                                    placeholder={selectedField.type === 'string' ? 'Máximo caracteres' : 'Valor máximo'}
                                />
                            </div>
                        )}
                        <div style={{ marginBottom: 10 }}>
                            <label>Leyenda (texto de ayuda)</label>
                            <textarea
                                value={selectedField.helpText ?? ''}
                                onChange={(e) => updateField(selectedField.id, { helpText: e.target.value })}
                                rows={2}
                            />
                        </div>
                    </>
                )}
            </div>
            </div>
        </div>
    );
}

export default App;
