import axios from "axios";
import { useRef, useState } from "react";
import ChatBot, { Button, Flow, Settings, Styles } from "react-chatbotify";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Chatbot from "../../assets/images/Chatbot.png";
import User from "../../assets/images/User.svg";
import "./ChatBot.css";
import Visualization from "./Visualization";
import { AgentApiResponse } from "../../interfaces/agentApiResponse";

const ChatBotWrapper = () => {
  const chatBotWrapperWindowRef = useRef<HTMLDivElement>(null);
  const [chatbotResponse, setchatbotResponse] = useState<any>(null);
  const [chartPayload, setChartPayload] = useState<{} | null>(null);
  const [chartDesign, setChartDesign] = useState<{} | null>(null);
  const options: string[] = [
    "Get me the movies released in 2000 with rating greater than 8",
    "Show me the top 5 movies with highest rating",
    "Get me the movies directed by Christopher Nolan",
    "Generate a bar chart of movie counts for each month in 2002",
  ];

  async function fetchResponse(
    query: string
  ): Promise<string | AgentApiResponse> {
    return new Promise((resolve) => {
      axios
        .post(
          `${import.meta.env.VITE_CHAT_API_URL}/query`,
          { query: query, localTimeStamp: new Date().toISOString() },
          {
            headers: {
              "Content-Type": "application/json",
              "Cache-Control": "no-cache",
            },
          }
        )
        .then((response) => {
          resolve(response.data);
        })
        .catch(() => {
          resolve("Error encountered. Please retry");
        });
    });
  }

  async function fetchResponseFromAgent(params: any) {
    if (params.userInput === "end") {
      await params.goToPath("end");
      setTimeout(() => params.openChat(false), 1000);
      return;
    }

    try {
      const response = (await fetchResponse(
        params.userInput
      )) as AgentApiResponse;
      if (response?.chart) {
        try {
          const chartData = JSON.parse(response.chart);
          setChartPayload(chartData?.data[0] || null);
          setChartDesign({
            ...chartData?.layout,
            autosize: true,
            responsive: true,
          });
        } catch (error) {
          console.error("Invalid chart data format:", error);
          setChartPayload(null);
          setChartDesign(null);
        }
        setchatbotResponse(response.answer || "");
      } else {
        setchatbotResponse(
          response.answer ||
            "Unable to answer your query. Could you try again with more information?"
        );
        setChartPayload(null);
      }

      await params.goToPath("reply");
    } catch (error) {
      console.error("API call failed:", error);
      setchatbotResponse(
        "I couldn't process your request. Could you provide more details and try again?"
      );
    }
  }
  
  const flow: Flow = {
    start: {
      message: "Hi, How can I assist you today?",
      path: "loop",
      options: options,
      chatDisabled: false,
    },
    loop: {
      message: async (params: any) => {
        await fetchResponseFromAgent(params);
      },
      path: "loop",
      options: [],
      chatDisabled: false,
    },
    reply: {
      component: (
        <div className="rcb-bot-message rcb-bot-message-entry">
          {chartPayload && chartDesign ? (
            <>
              <div className="customMarkDown">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[remarkGfm]}
                >
                  {chatbotResponse}
                </ReactMarkdown>
              </div>
              <Visualization
                data={[chartPayload]}
                layout={chartDesign}
              />
            </>
          ) : (
            <div className="customMarkDown">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[remarkGfm]}
              >
                {chatbotResponse}
              </ReactMarkdown>
            </div>
          )}
        </div>
      ),
      path: "loop",
      options: options,
    },
    end: {
      message: "This conversation is closed. Thank you",
      chatDisabled: false,
      path: "start",
      options: [],
    },
  };

  const DefaultSettings: Settings = {
    general: {
      fontFamily:
        "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', " +
        "'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', " +
        "sans-serif",
      showHeader: true,
      showFooter: false,
      showInputRow: true,
      embedded: true,
      flowStartTrigger: "ON_LOAD",
    },
    tooltip: {
      mode: "ALWAYS",
      text: "Talk to the Chatbot",
    },
    header: {
      title: (
        <div
          style={{
            cursor: "pointer",
            margin: 0,
            fontSize: 16,
            fontWeight: "bold",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <img src={Chatbot} alt="Chabot Icon" height={32} />
          Movie Mate
        </div>
      ),
      showAvatar: false,
      buttons: [Button.NOTIFICATION_BUTTON, Button.CLOSE_CHAT_BUTTON],
    },
    notification: {
      disabled: true,
    },
    audio: {
      disabled: true,
    },
    ariaLabel: {
      chatButton: "ChatBot",
    },
    chatHistory: {
      disabled: true,
    },
    chatInput: {
      disabled: false,
      allowNewline: false,
      enabledPlaceholderText: "Type your question...",
      disabledPlaceholderText: "",
      showCharacterCount: true,
      characterLimit: -1,
      botDelay: 500,
      blockSpam: true,
      sendOptionOutput: true,
      sendCheckboxOutput: true,
    },
    chatWindow: {
      showScrollbar: false,
      autoJumpToBottom: true,
      showMessagePrompt: true,
      messagePromptText: "New Messages ↓",
      messagePromptOffset: 30,
      defaultOpen: true,
    },
    sensitiveInput: {
      maskInTextArea: true,
      maskInUserBubble: true,
      asterisksCount: 10,
      hideInUserBubble: false,
    },
    chatButton: {
      icon: Chatbot,
    },
    userBubble: {
      animate: true,
      avatar: User,
      showAvatar: true,
      simStream: false,
      streamSpeed: 30,
      dangerouslySetInnerHtml: true,
    },
    botBubble: {
      animate: true,
      avatar: Chatbot,
      showAvatar: true,
      simStream: false,
      streamSpeed: 30,
      dangerouslySetInnerHtml: false,
    },
    voice: {
      disabled: false,
    },
    fileAttachment: {
      disabled: false,
    },
    toast: {
      maxCount: 3,
      forbidOnMax: false,
      dismissOnClick: true,
    },
  };
  const DefaultStyles: Styles = {
    botOptionStyle: {
      fontSize: "15px",
      padding: "5px 10px",
      backgroundColor: "rgb(108, 104, 113)",
      color: "white",
    },
    botOptionHoveredStyle: {
      fontSize: "15px",
      padding: "5px 10px",
      backgroundColor: "Highlight",
      borderBlockColor: "Highlight",
    },
    voiceButtonStyle: {
      borderRadius: "50%",
    },
    voiceButtonDisabledStyle: {
      borderRadius: "50%",
    },
    chatIconStyle: {
      backgroundImage: `url(${Chatbot})`,
      height: "30px",
      width: "40px",
      backgroundRepeat: "no-repeat",
      marginLeft: "11%",
    },
    tooltipStyle: {
      fontSize: "15px",
    },
  };

  return (
    <div ref={chatBotWrapperWindowRef} className="custom-chat-window">
      <ChatBot settings={DefaultSettings} styles={DefaultStyles} flow={flow} />
    </div>
  );
};
export default ChatBotWrapper;
