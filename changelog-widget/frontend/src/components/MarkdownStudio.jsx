/**
 * components/MarkdownStudio.jsx
 * ─────────────────────────────
 * Split-screen Markdown Studio for creating and editing changelog posts.
 * Left: Structured metadata inputs (title, category, version, status, scheduled date) + Markdown editor.
 * Right: Live, real-time rendered preview matching the public Changelog UI.
 */
import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import changelogService from '../services/changelogService'
import { Button, Input, Select, Textarea, Badge } from '../components/ui'
import './MarkdownStudio.css'

const CATEGORIES = [
  { value: 'NEW', label: 'New Feature', badgeClass: 'badge-new' },
  { value: 'IMPROVED', label: 'Improvement', badgeClass: 'badge-improved' },
  { value: 'FIXED', label: 'Bug Fix', badgeClass: 'badge-fixed' },
]

export default function MarkdownStudio({
  initialData = null,
  onSave,
  onPublish,
  onCancel,
  isSaving = false,
}) {
  const [title, setTitle] = useState(initialData?.title || '')
  const [category, setCategory] = useState(initialData?.category || 'NEW')
  const [version, setVersion] = useState(initialData?.version || '')
  const [status, setStatus] = useState(initialData?.status || 'DRAFT')
  const [scheduledFor, setScheduledFor] = useState(
    initialData?.scheduled_for
      ? new Date(initialData.scheduled_for).toISOString().slice(0, 16)
      : ''
  )
  const [coverImage, setCoverImage] = useState(initialData?.cover_image || '')
  const [contentMarkdown, setContentMarkdown] = useState(
    initialData?.content_markdown ||
      '## What changed\n\n- Detailed description of the feature or fix\n- Performance improvements and UI tweaks\n\n```javascript\n// Example usage\nconst client = new ChangelogWidget();\n```'
  )
  const [activeTab, setActiveTab] = useState('split') // 'split', 'edit', 'preview' on mobile
  const [isUploadingCover, setIsUploadingCover] = useState(false)
  const [isUploadingInline, setIsUploadingInline] = useState(false)
  const [uploadError, setUploadError] = useState('')

  const handleCoverFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setIsUploadingCover(true)
    setUploadError('')
    try {
      const res = await changelogService.uploadImage(file)
      setCoverImage(res.url)
    } catch (err) {
      setUploadError(err.response?.data?.detail || 'Failed to upload cover image.')
    } finally {
      setIsUploadingCover(false)
      e.target.value = ''
    }
  }

  const handleInlineFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setIsUploadingInline(true)
    setUploadError('')
    try {
      const res = await changelogService.uploadImage(file)
      insertMarkdown(`\n![${file.name.replace(/\.[^/.]+$/, '')}](${res.url})\n`)
    } catch (err) {
      setUploadError(err.response?.data?.detail || 'Failed to upload image into markdown.')
    } finally {
      setIsUploadingInline(false)
      e.target.value = ''
    }
  }

  useEffect(() => {
    if (initialData) {
      setTitle(initialData.title || '')
      setCategory(initialData.category || 'NEW')
      setVersion(initialData.version || '')
      setStatus(initialData.status || 'DRAFT')
      setScheduledFor(
        initialData.scheduled_for
          ? new Date(initialData.scheduled_for).toISOString().slice(0, 16)
          : ''
      )
      setCoverImage(initialData.cover_image || '')
      setContentMarkdown(initialData.content_markdown || '')
    }
  }, [initialData])

  // Helper to insert markdown tags at cursor
  const insertMarkdown = (prefix, suffix = '') => {
    const textarea = document.getElementById('studio-markdown-editor')
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const text = textarea.value
    const selected = text.substring(start, end)
    const replacement = prefix + selected + suffix

    const nextText =
      text.substring(0, start) + replacement + text.substring(end)
    setContentMarkdown(nextText)

    setTimeout(() => {
      textarea.focus()
      textarea.setSelectionRange(
        start + prefix.length,
        start + prefix.length + selected.length
      )
    }, 0)
  }

  const buildPayload = (explicitStatus = null) => {
    const finalStatus = explicitStatus || status
    const payload = {
      title: title.trim(),
      category,
      cover_image: coverImage.trim() || null,
      content_markdown: contentMarkdown,
      version: version.trim() || null,
      status: finalStatus,
    }

    if (finalStatus === 'SCHEDULED' && scheduledFor) {
      payload.scheduled_for = new Date(scheduledFor).toISOString()
    } else if (finalStatus !== 'SCHEDULED') {
      payload.scheduled_for = null
    }

    return payload
  }

  const handleSave = (e) => {
    if (e) e.preventDefault()
    if (!title.trim()) {
      alert('Please provide a title for the changelog.')
      return
    }
    if (status === 'SCHEDULED' && !scheduledFor) {
      alert('Please specify a scheduled publish date and time.')
      return
    }
    onSave(buildPayload())
  }

  const handlePublishNow = (e) => {
    if (e) e.preventDefault()
    if (!title.trim()) {
      alert('Please provide a title for the changelog.')
      return
    }
    onPublish(buildPayload('PUBLISHED'))
  }

  return (
    <div className="markdown-studio-container">
      {/* Studio Header / Action Bar */}
      <div className="studio-navbar">
        <div className="studio-navbar-left">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onCancel}
            title="Return to list"
          >
            ← Back
          </Button>
          <div className="studio-title-block">
            <span className="studio-badge-mode">
              {initialData ? 'Editing Changelog' : 'New Changelog'}
            </span>
            <span className="studio-subtitle">
              {title ? title : 'Untitled Entry'}
            </span>
          </div>
        </div>

        <div className="studio-view-toggle">
          <Button
            type="button"
            variant={activeTab === 'split' ? 'default' : 'ghost'}
            size="sm"
            className={`toggle-btn ${activeTab === 'split' ? 'active' : ''}`}
            onClick={() => setActiveTab('split')}
          >
            Split View
          </Button>
          <Button
            type="button"
            variant={activeTab === 'edit' ? 'default' : 'ghost'}
            size="sm"
            className={`toggle-btn ${activeTab === 'edit' ? 'active' : ''}`}
            onClick={() => setActiveTab('edit')}
          >
            Editor Only
          </Button>
          <Button
            type="button"
            variant={activeTab === 'preview' ? 'default' : 'ghost'}
            size="sm"
            className={`toggle-btn ${activeTab === 'preview' ? 'active' : ''}`}
            onClick={() => setActiveTab('preview')}
          >
            Preview Only
          </Button>
        </div>

        <div className="studio-navbar-actions">
          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={handleSave}
            disabled={isSaving}
          >
            {isSaving
              ? 'Saving...'
              : status === 'SCHEDULED'
              ? '⏰ Save Scheduled'
              : status === 'PUBLISHED'
              ? '💾 Save Changes'
              : '📝 Save Draft'}
          </Button>

          {status !== 'PUBLISHED' && (
            <Button
              type="button"
              variant="default"
              size="sm"
              className="btn-publish"
              onClick={handlePublishNow}
              disabled={isSaving}
            >
              {isSaving ? 'Publishing...' : '🚀 Publish Now'}
            </Button>
          )}
        </div>
      </div>

      {/* Main Split Body */}
      <div className={`studio-split-body tab-${activeTab}`}>
        {/* Left Column: Editor & Inputs */}
        <div className="studio-editor-pane">
          <div className="studio-field-group">
            <label className="field-label" htmlFor="studio-title">
              Update Title <span className="text-danger">*</span>
            </label>
            <Input
              id="studio-title"
              type="text"
              className="studio-input-title"
              placeholder="e.g., Lightning Fast Search & Filter 2.0"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="studio-meta-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))' }}>
            <div className="studio-field-group">
              <label className="field-label" htmlFor="studio-category">
                Category
              </label>
              <Select
                id="studio-category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                {CATEGORIES.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label} ({c.value})
                  </option>
                ))}
              </Select>
            </div>

            <div className="studio-field-group">
              <label className="field-label" htmlFor="studio-version">
                Version Release (optional)
              </label>
              <Input
                id="studio-version"
                type="text"
                placeholder="e.g. v2.1.0"
                value={version}
                onChange={(e) => setVersion(e.target.value)}
              />
            </div>

            <div className="studio-field-group">
              <label className="field-label" htmlFor="studio-status">
                Status
              </label>
              <Select
                id="studio-status"
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              >
                <option value="DRAFT">📝 Draft</option>
                <option value="SCHEDULED">⏰ Scheduled</option>
                <option value="PUBLISHED">🚀 Published</option>
              </Select>
            </div>

            {status === 'SCHEDULED' && (
              <div className="studio-field-group">
                <label className="field-label" htmlFor="studio-scheduled-for">
                  Publish Date & Time <span className="text-danger">*</span>
                </label>
                <Input
                  id="studio-scheduled-for"
                  type="datetime-local"
                  value={scheduledFor}
                  onChange={(e) => setScheduledFor(e.target.value)}
                  required
                />
              </div>
            )}
          </div>

          <div className="studio-field-group">
            <label className="field-label" htmlFor="studio-cover">
              Cover Image (Upload or URL)
            </label>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <Input
                id="studio-cover"
                type="text"
                placeholder="https://... or click Upload"
                value={coverImage}
                onChange={(e) => setCoverImage(e.target.value)}
                style={{ flex: 1 }}
              />
              <label
                className="btn btn-secondary btn-sm"
                style={{ cursor: 'pointer', whiteSpace: 'nowrap' }}
                title="Upload image from computer"
              >
                {isUploadingCover ? '⏳ Uploading...' : '📁 Upload'}
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp,image/gif"
                  style={{ display: 'none' }}
                  onChange={handleCoverFileChange}
                  disabled={isUploadingCover}
                />
              </label>
              {coverImage && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setCoverImage('')}
                  title="Remove image"
                >
                  ✕
                </Button>
              )}
            </div>
            {uploadError && (
              <span className="text-danger" style={{ fontSize: '0.8rem', marginTop: '4px', display: 'block' }}>
                {uploadError}
              </span>
            )}
          </div>

          {/* Markdown Toolbar */}
          <div className="studio-toolbar">
            <button
              type="button"
              className="tool-btn"
              onClick={() => insertMarkdown('**', '**')}
              title="Bold"
            >
              <b>B</b>
            </button>
            <button
              type="button"
              className="tool-btn"
              onClick={() => insertMarkdown('*', '*')}
              title="Italic"
            >
              <i>I</i>
            </button>
            <span className="tool-divider" />
            <button
              type="button"
              className="tool-btn"
              onClick={() => insertMarkdown('## ')}
              title="Heading 2"
            >
              H2
            </button>
            <button
              type="button"
              className="tool-btn"
              onClick={() => insertMarkdown('### ')}
              title="Heading 3"
            >
              H3
            </button>
            <span className="tool-divider" />
            <button
              type="button"
              className="tool-btn"
              onClick={() => insertMarkdown('- ')}
              title="Bullet list"
            >
              • List
            </button>
            <button
              type="button"
              className="tool-btn"
              onClick={() => insertMarkdown('1. ')}
              title="Numbered list"
            >
              1. List
            </button>
            <button
              type="button"
              className="tool-btn"
              onClick={() => insertMarkdown('> ')}
              title="Quote"
            >
              ❝
            </button>
            <span className="tool-divider" />
            <button
              type="button"
              className="tool-btn"
              onClick={() => insertMarkdown('`', '`')}
              title="Inline Code"
            >
              &lt;/&gt;
            </button>
            <button
              type="button"
              className="tool-btn"
              onClick={() => insertMarkdown('```\n', '\n```')}
              title="Code Block"
            >
              Code Block
            </button>
            <button
              type="button"
              className="tool-btn"
              onClick={() => insertMarkdown('[', '](url)')}
              title="Link"
            >
              🔗 Link
            </button>
            <label
              className="tool-btn"
              style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center' }}
              title="Upload an image and insert into markdown"
            >
              {isUploadingInline ? '⏳ Uploading...' : '📎 Upload Image'}
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp,image/gif"
                style={{ display: 'none' }}
                onChange={handleInlineFileChange}
                disabled={isUploadingInline}
              />
            </label>
            <button
              type="button"
              className="tool-btn"
              onClick={() => insertMarkdown('![Alt](', ')')}
              title="Image"
            >
              🖼️ Image
            </button>
          </div>

          <div className="studio-textarea-wrapper">
            <Textarea
              id="studio-markdown-editor"
              className="studio-markdown-textarea"
              placeholder="Write your release notes in Markdown..."
              value={contentMarkdown}
              onChange={(e) => setContentMarkdown(e.target.value)}
            />
          </div>
        </div>

        {/* Right Column: Live Rendered Preview */}
        <div className="studio-preview-pane">
          <div className="studio-preview-header">
            <span className="studio-preview-indicator">
              <span className="indicator-dot"></span> LIVE PREVIEW
            </span>
          </div>

          <div className="studio-preview-content">
            {coverImage && (
              <div className="studio-preview-cover">
                <img
                  src={coverImage}
                  alt="Cover preview"
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
              </div>
            )}

            <div className="studio-preview-tags" style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <Badge
                variant={
                  category === 'NEW'
                    ? 'default'
                    : category === 'IMPROVED'
                    ? 'secondary'
                    : 'outline'
                }
                className={
                  category === 'NEW'
                    ? 'badge-new'
                    : category === 'IMPROVED'
                    ? 'badge-improved'
                    : 'badge-fixed'
                }
              >
                {category}
              </Badge>

              {version && (
                <span className="version-pill" style={{
                  fontSize: '0.75rem',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  background: 'var(--color-accent-dim)',
                  color: 'var(--color-accent)',
                  fontWeight: 600,
                }}>
                  {version}
                </span>
              )}

              {status === 'SCHEDULED' && (
                <Badge variant="outline" style={{ borderColor: 'var(--color-warning)', color: 'var(--color-warning)' }}>
                  ⏰ Scheduled {scheduledFor ? `for ${new Date(scheduledFor).toLocaleDateString()}` : ''}
                </Badge>
              )}

              <span className="preview-date">
                {new Date().toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </span>
            </div>

            <h1 className="preview-title">
              {title || <span style={{ color: 'var(--color-text-muted)' }}>Your Update Title Here</span>}
            </h1>

            <div className="markdown-body preview-markdown">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {contentMarkdown || '*No content yet.*'}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
