import axios from "axios";
import { useEffect, useRef, useState } from "react";
import ChatBot, { Button, Flow, Settings, Styles } from "react-chatbotify";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Chatbot from "../../assets/images/Chatbot.png";
import User from "../../assets/images/User.svg";
import "./CustomChatBot.css";

const CustomChatBot = () => {
  const customChatWindowRef = useRef<HTMLDivElement>(null);
  const [currComp, setcurrComp] = useState<any>(null);
  const [scrollWidth, setScrollWidth] = useState(0);
  const [scrollHeight, setScrollHeight] = useState(0);

  useEffect(() => {
    const checkScrollWidth = () => {
      const element = document.getElementsByClassName("rcb-chat-window")[0];
      if (element) {
        const currentScrollWidth = element.scrollWidth;
        const currentScrollHeight = element.scrollHeight;
        // Check if the scroll width has changed
        if (currentScrollWidth !== scrollWidth) {
          setScrollWidth(currentScrollWidth);
        }
        if (currentScrollHeight !== scrollHeight) {
          setScrollHeight(currentScrollHeight);
        }
      }
    };

    // Set interval to check for scroll width changes every 100ms
    const intervalId = setInterval(checkScrollWidth, 100);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, [scrollWidth, scrollHeight]);

  const suggestions: Array<string> = [];
  function fetchResponse(query: string) {
    return new Promise((resolve) => {
      axios
        .post(
          `${import.meta.env.VITE_CHAT_API_URL}/query`,
          { query: query, localTimeStamp: new Date().toISOString() },
          {
            headers: {
              "Content-Type": "application/json",
              "Cache-Control": "no-cache",
              "Ocp-Apim-Subscription-Key": import.meta.env.VITE_GENAI_SUBSCRIPTION_ID
            }
          }
        )
        .then((data) => {
          resolve(data.data);
        })
        .catch(() => {
          resolve("Something went wrong. Try Again.");
        });
    });
  }

  type ApiResponse = {
    reviewImage: any;
    chart: string;
    answer: string;
  };

  const call_LlmApi = async (params: any) => {
    if (params.userInput === "end") {
      await params.goToPath("end");
      await setTimeout(() => params.openChat(false), 1000);
      return;
    }

    try {
      const response = (await fetchResponse(params.userInput)) as ApiResponse;

     if (response?.reviewImage && response?.answer) {
        setcurrComp(
          response.answer ||
            "Unable to answer your query. Could you try again with more information?"
        );
      }

      await params.goToPath("reply");
    } catch (error) {
      console.error("API call failed:", error);
      setcurrComp("Unable to answer your query. Could you try again with more information?");
    }
  }; 
  const flow: Flow = {
    start: {
      message: "Hi, How can I help you today?",
      path: "loop",
      options: suggestions,
      chatDisabled: false
    },
    loop: {
      message: async (params: any) => {
        await call_LlmApi(params);
      },
      path: "loop",
      options: [],
      chatDisabled: false
    },
    reply: {
      component: (
        <div className="rcb-bot-message rcb-bot-message-entry">
            <div className="customMarkDown">
              <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[remarkGfm]}>
                {currComp}
              </ReactMarkdown>
            </div>
        </div>
      ),
      path: "loop",
      options: suggestions
    },
    end: {
      message: "This conversation is closed. Thank you",
      chatDisabled: false,
      path: "start",
      options: []
    }
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
      flowStartTrigger: "ON_LOAD"
    },
    tooltip: {
      mode: "ALWAYS",
      text: "Chat with the file analyzer bot"
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
            gap: "10px"
          }}>
          <img src={Chatbot} alt="Chabot Icon" height={32} />
          File Analyzer
        </div>
      ),
      showAvatar: false,
      buttons: [
        Button.NOTIFICATION_BUTTON,
        Button.CLOSE_CHAT_BUTTON,
      ]
    },
    notification: {
      disabled: true
    },
    audio: {
      disabled: true
    },
    ariaLabel: {
      chatButton: "ChatBot"
    },
    chatHistory: {
      disabled: true
    },
    chatInput: {
      disabled: false,
      allowNewline: false,
      enabledPlaceholderText: "Type your query...",
      disabledPlaceholderText: "",
      showCharacterCount: true,
      characterLimit: -1,
      botDelay: 500,
      blockSpam: true,
      sendOptionOutput: true,
      sendCheckboxOutput: true
    },
    chatWindow: {
      showScrollbar: false,
      autoJumpToBottom: true,
      showMessagePrompt: true,
      messagePromptText: "New Messages ↓",
      messagePromptOffset: 30,
      defaultOpen: true
    },
    sensitiveInput: {
      maskInTextArea: true,
      maskInUserBubble: true,
      asterisksCount: 10,
      hideInUserBubble: false
    },
    chatButton: {
      icon: Chatbot
    },
    userBubble: {
      animate: true,
      avatar: User,
      showAvatar: true,
      simStream: false,
      streamSpeed: 30,
      dangerouslySetInnerHtml: true
    },
    botBubble: {
      animate: true,
      avatar: Chatbot,
      showAvatar: true,
      simStream: false,
      streamSpeed: 30,
      dangerouslySetInnerHtml: false
    },
    voice: {
      disabled: false
    },
    fileAttachment: {
      disabled: false,

    },
    toast: {
      maxCount: 3,
      forbidOnMax: false,
      dismissOnClick: true
    }
  };
  const DefaultStyles: Styles = {
    botOptionStyle: {
      fontSize: "15px",
      padding: "5px 10px",
      backgroundColor: "rgb(108, 104, 113)",
      color: "white"
    },
    botOptionHoveredStyle: {
      fontSize: "15px",
      padding: "5px 10px",
      backgroundColor: "Highlight",
      borderBlockColor: "Highlight"
    },
    voiceButtonStyle: {
      borderRadius: "50%"
    },
    voiceButtonDisabledStyle: {
      borderRadius: "50%"
    },
    chatIconStyle: {
      backgroundImage: `url(${Chatbot})`,
      height: "30px",
      width: "40px",
      backgroundRepeat: "no-repeat",
      marginLeft: "11%"
    },
    tooltipStyle: {
      fontSize: "15px",
    }
  };

  return (
    <div
      ref={customChatWindowRef}
      className="custom-chat-window">
      <ChatBot settings={DefaultSettings} styles={DefaultStyles} flow={flow} />
    </div>
  );
};
export default CustomChatBot;
