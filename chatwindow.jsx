// ChatWindow.js
import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import configData from '../config';
import { IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import MinimizeIcon from '@mui/icons-material/Minimize';

const ChatWindow = ({ setChatOpen }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isOpen, setIsOpen] = useState(true);
    const [ws,setWs] = useState(null);

    const account = useSelector((state) => state.account);
    const { role, token } = account;

    useEffect(() => {
        if(role == 'AppAdmin'){
            // let currentRecipient = null;
            const chatSocket = new WebSocket(configData.WS_SERVER + 'ws/chat/?token=' + token);
            console.log('WebSocket URL inside'); 
            chatSocket.onopen = () => {
                console.log('WebSocket connection established');
                setWs(chatSocket);
            }

            chatSocket.onerror = () => {
                console.log('WebSocket connection failed with error');
            }
    
            chatSocket.onclose = () => {
                console.log('WebSocket connection closed inside onclose()');
                setWs(null); 
            }
    
            chatSocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log('WebSocket message received:', data);
                setMessages([...messages, { text: data.message, sender: data.username }])
            }
        } else if(role == 'Driver') {
            const chatSocket = new WebSocket(configData.WS_SERVER + 'ws/chat/?token=' + token);
            console.log('WebSocket URL inside'); 
            chatSocket.onopen = () => {
                console.log('WebSocket connection established');
                setWs(chatSocket);
            }
    
            chatSocket.onclose = () => {
                console.log('WebSocket connection closed inside onclose()');
                setWs(null); 
            }

            chatSocket.onerror = () => {
                console.log('WebSocket connection failed with error');
            }

            chatSocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log('WebSocket message received:', data);
                setMessages([...messages, { text: data.message, sender: data.username }])
            }
        }
    }, [])


    // let currentRecipient = null;
    // const chatSocket = new WebSocket(
    //     "ws://" + window.location.host + "/ws/chat/"
    // );

    // chatSocket.onopen = function(e) {
    //     console.log("Connection established.");
    // };

    // chatSocket.onclose = function(e) {
    //     console.error("WebSocket closed unexpectedly:", e);
    // };

    // chatSocket.onerror = function(e) {
    //     console.error("WebSocket error observed:", e);
    // };

    // chatSocket.onmessage = function(e) {
    //     const data = JSON.parse(e.data);
    //     const div = document.createElement("div");
    //     div.innerHTML = data.username + ": " + data.message;
    //     div.classList.add('message');
    //     div.style.cursor = 'pointer';
    //     document.querySelector("#message_list").appendChild(div);

    //     div.onclick = function() {
    //         currentRecipient = data.username;
    //         document.querySelector("#chat_box").style.display = "block";
    //         document.querySelector("#message_input").focus();
    //     };
    // };

    // document.querySelector("#send_button").onclick = function(e) {
    //     const messageInput = document.querySelector("#message_input");
    //     const message = messageInput.value;

    //     chatSocket.send(JSON.stringify({
    //         "message": message,
    //         "recipient": currentRecipient
    //     }));

    //     if (message.trim() !== "") {
    //         chatSocket.send(JSON.stringify({
    //             "message": message,
    //             "recipient": "admin"
    //         }));

    //     messageInput.value = "";
    //     }
    // };
    const handleInputChange = (e) => {
        setInput(e.target.value);
    };

    const handleSendMessage = () => {
        if (input.trim()) {
            setMessages([...messages, { text: input, sender: 'You' }]);
            console.log('sending Message')
            ws.send(JSON.stringify({
                'message': input,
                'recipient': 'AppAdmin'
            }))
            setInput('');
        }
    };

    function handleChatClose(){
        setChatOpen(false);
        if(ws){
            ws.close();
        }
        setWs(null);
    }

    return (
        <div className={`chat-container ${isOpen ? 'open' : ''}`}>
            <div className="chat-header">
                Chat with us
                <div className="chat-controls">
                    <IconButton size="small" onClick={() => setIsOpen(!isOpen)}>
                        <MinimizeIcon style={{ color: 'white' }} />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleChatClose()}>
                        <CloseIcon style={{ color: 'white' }} />
                    </IconButton>
                </div>
            </div>
            {isOpen && (
                <div className="chat-body">
                    <div className="messages">
                        {messages.map((msg, index) => (
                            <div key={index} className={`message ${msg.sender}`}>
                                {msg.sender + ': ' + msg.text}
                            </div>
                        ))}
                    </div>
                    <div className="chat-input">
                        <input 
                            type="text" 
                            value={input} 
                            onChange={handleInputChange} 
                            placeholder="Type your message..." 
                        />
                        <button onClick={handleSendMessage}>Send</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ChatWindow;



// second version //////////////////////////////////////////////////////////////////


// import React, { useState, useEffect } from 'react';
// import { useSelector } from 'react-redux';
// import configData from '../config';
// import { IconButton } from '@mui/material';
// import CloseIcon from '@mui/icons-material/Close';
// import MinimizeIcon from '@mui/icons-material/Minimize';

// const ChatWindow = ({ setChatOpen }) => {
//     const [messages, setMessages] = useState([]);
//     const [input, setInput] = useState('');
//     const [isOpen, setIsOpen] = useState(true);
//     const [ws, setWs] = useState(null);
//     const [selectedUser, setSelectedUser] = useState(null);

//     const account = useSelector((state) => state.account);
//     const { role, token } = account;

//     useEffect(() => {
//         const chatSocket = new WebSocket(configData.WS_SERVER + 'ws/chat/?token=' + token);

//         chatSocket.onopen = () => {
//             console.log('WebSocket connection established');
//             setWs(chatSocket);
//         }

//         chatSocket.onerror = () => {
//             console.log('WebSocket connection failed with error');
//         }

//         chatSocket.onclose = () => {
//             console.log('WebSocket connection closed');
//             setWs(null);
//         }

//         chatSocket.onmessage = (event) => {
//             const data = JSON.parse(event.data);
//             console.log('WebSocket message received:', data);
//             setMessages(prevMessages => [...prevMessages, { text: data.message, sender: data.username }]);
//         }

//         return () => {
//             chatSocket.close();
//         };
//     }, [token]);

//     const handleInputChange = (e) => {
//         setInput(e.target.value);
//     };

//     const handleSendMessage = () => {
//         if (input.trim()) {
//             setMessages([...messages, { text: input, sender: 'You' }]);
//             ws.send(JSON.stringify({
//                 'message': input,
//                 'recipient': selectedUser || 'admin'
//             }));
//             setInput('');
//         }
//     };

//     const handleChatClose = () => {
//         setChatOpen(false);
//         if (ws) {
//             ws.close();
//         }
//         setWs(null);
//     };

//     const handleUserSelect = (username) => {
//         setSelectedUser(username);
//         setMessages([]);
//     };

//     return (
//         <div className={`chat-container ${isOpen ? 'open' : ''}`}>
//             <div className="chat-header">
//                 Chat with us
//                 <div className="chat-controls">
//                     <IconButton size="small" onClick={() => setIsOpen(!isOpen)}>
//                         <MinimizeIcon style={{ color: 'white' }} />
//                     </IconButton>
//                     <IconButton size="small" onClick={() => handleChatClose()}>
//                         <CloseIcon style={{ color: 'white' }} />
//                     </IconButton>
//                 </div>
//             </div>
//             {isOpen && (
//                 <div className="chat-body">
//                     <div className="messages">
//                         {messages.map((msg, index) => (
//                             <div
//                                 key={index}
//                                 className={`message ${msg.sender}`}
//                                 onClick={() => role.includes('Admin') && handleUserSelect(msg.sender)}
//                             >
//                                 {msg.sender + ': ' + msg.text}
//                             </div>
//                         ))}
//                     </div>
//                     <div className="chat-input">
//                         <input
//                             type="text"
//                             value={input}
//                             onChange={handleInputChange}
//                             placeholder="Type your message..."
//                         />
//                         <button onClick={handleSendMessage}>Send</button>
//                     </div>
//                 </div>
//             )}
//         </div>
//     );
// };

// export default ChatWindow;



// Version 3 worked well //////////////////////////////////////////////////////////////////////////////

// import React, { useState, useEffect } from 'react';
// import { useSelector } from 'react-redux';
// import configData from '../config';
// import { IconButton } from '@mui/material';
// import CloseIcon from '@mui/icons-material/Close';
// import MinimizeIcon from '@mui/icons-material/Minimize';

// const ChatWindow = ({ setChatOpen }) => {
//     const [messages, setMessages] = useState([]);
//     const [input, setInput] = useState('');
//     const [isOpen, setIsOpen] = useState(true);
//     const [ws, setWs] = useState(null);
//     const [selectedUser, setSelectedUser] = useState(null);

//     const account = useSelector((state) => state.account);
//     const { role, token } = account;

//     useEffect(() => {
//         const chatSocket = new WebSocket(configData.WS_SERVER + 'ws/chat/?token=' + token);

//         chatSocket.onopen = () => {
//             console.log('WebSocket connection established');
//             setWs(chatSocket);
//         }

//         chatSocket.onerror = () => {
//             console.log('WebSocket connection failed with error');
//         }

//         chatSocket.onclose = () => {
//             console.log('WebSocket connection closed');
//             setWs(null); 
//         }

//         chatSocket.onmessage = (event) => {
//             const data = JSON.parse(event.data);
//             console.log('WebSocket message received:', data);
//             setMessages(prevMessages => [...prevMessages, { text: data.message, sender: data.username }]);
//         }

//         return () => {
//             chatSocket.close();
//         };
//     }, [token]);

//     const handleInputChange = (e) => {
//         setInput(e.target.value);
//     };

//     const handleSendMessage = () => {
//         if (input.trim()) {
//             setMessages([...messages, { text: input, sender: 'You' }]);
//             ws.send(JSON.stringify({
//                 'message': input,
//                 'recipient': selectedUser || 'admin'
//             }));
//             setInput('');
//         }
//     };

//     const handleChatClose = () => {
//         setChatOpen(false);
//         if (ws) {
//             ws.close();
//         }
//         setWs(null);
//     };

//     const handleUserSelect = (username) => {
//         setSelectedUser(username);
//         setMessages([]);
//     };

//     return (
//         <div className={`chat-container ${isOpen ? 'open' : ''}`}>
//             <div className="chat-header">
//                 Chat with us
//                 <div className="chat-controls">
//                     <IconButton size="small" onClick={() => setIsOpen(!isOpen)}>
//                         <MinimizeIcon style={{ color: 'white' }} />
//                     </IconButton>
//                     <IconButton size="small" onClick={() => handleChatClose()}>
//                         <CloseIcon style={{ color: 'white' }} />
//                     </IconButton>
//                 </div>
//             </div>
//             {isOpen && (
//                 <div className="chat-body">
//                     <div className="messages">
//                         {messages.map((msg, index) => (
//                             <div 
//                                 key={index} 
//                                 className={`message ${msg.sender}`}
//                                 onClick={() => role.includes('Admin') && handleUserSelect(msg.sender)}
//                             >
//                                 {msg.sender + ': ' + msg.text}
//                             </div>
//                         ))}
//                     </div>
//                     <div className="chat-input">
//                         <input 
//                             type="text" 
//                             value={input} 
//                             onChange={handleInputChange} 
//                             placeholder="Type your message..." 
//                         />
//                         <button onClick={handleSendMessage}>Send</button>
//                     </div>
//                 </div>
//             )}
//         </div>
//     );
// };

// export default ChatWindow;


