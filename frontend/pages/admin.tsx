import ChatWindow from "../components/ChatWindow";

export default function Admin() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>
      <ChatWindow demo={false} />
    </div>
  );
}
