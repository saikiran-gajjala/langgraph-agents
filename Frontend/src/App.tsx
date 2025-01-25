import "./App.css";
import CustomChatBot from "./components/ChatBot/CustomChatBot";

function App() {
  return (
    <>
      <div
        className="container"
      >
        <div  className="chatbot-component">
          <CustomChatBot />
        </div>
      </div>
    </>
  );
}

export default App;
