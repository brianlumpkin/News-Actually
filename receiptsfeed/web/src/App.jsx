import StoryCard from './components/StoryCard.jsx'

export default function App() {
  const demo = [
    { title: "Demo Story A", link: "#" },
    { title: "Demo Story B", link: "#" },
  ];
  return (
    <div style={{ padding: 16, fontFamily: 'system-ui, sans-serif' }}>
      <h1>receiptsfeed — demo</h1>
      {demo.map((s, i) => <StoryCard key={i} story={s} />)}
    </div>
  );
}
