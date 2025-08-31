import ChatWindow from "../components/ChatWindow";

export default function Home() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Kick Chatbot Demo</h1>
      <ChatWindow demo={true} />
    </div>
  );
}
