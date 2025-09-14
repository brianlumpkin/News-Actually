export default function StoryCard({ story }) {
  return (
    <a href={story.link} style={{ display:'block', padding:12, margin:'8px 0', border:'1px solid #ddd', borderRadius:8, textDecoration:'none', color:'#111' }}>
      <strong>{story.title}</strong>
    </a>
  )
}
