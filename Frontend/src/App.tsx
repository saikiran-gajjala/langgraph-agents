import "./App.css";
import CustomChatBot from "./components/ChatBot/CustomChatBot";
import FileUpload from "./components/Fileupload/Fileupload";

function App() {
  return (
    <>
      <div
        className="container"
      >
        <div className="fileuploader-component">
          <FileUpload />
        </div>
        <div  className="chatbot-component">
          <CustomChatBot />
        </div>
      </div>
    </>
  );
}

export default App;
