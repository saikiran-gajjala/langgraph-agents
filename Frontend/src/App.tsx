import "./App.css";
import ChatBotWrapper from "./components/ChatBot/ChatBot";

function App() {
  return (
    <>
      <div
        className="container"
      >
        <div  className="chatbot-component">
          <ChatBotWrapper />
        </div>
      </div>
    </>
  );
}

export default App;
