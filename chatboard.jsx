// import React, { useState, useEffect, useRef } from 'react';
// import { Grid, List, ListItem, ListItemText, Paper, Typography, Box, IconButton, InputBase, Divider } from '@mui/material';
// import CloseIcon from '@mui/icons-material/Close';
// import SendIcon from '@mui/icons-material/Send';
// import configData from '../config';
// import axios from 'axios';
// import { useSelector } from 'react-redux';
// import { makeStyles } from '@material-ui/styles';
// import colors from '../assets/scss/_themes-vars.module.scss';

// const useStyles = makeStyles((theme) => ({
//     selected: {
//         backgroundColor: '#71e0f9',
//         '&:hover': {
//             backgroundColor: '#71e0f9',
//         },
//     },
// }));

// const ChatBoard = () => {
//     const [message, setMessage] = useState('');
//     const [chatRoom, setChatRoom] = useState([]);
//     const [chatMessages, setChatMessages] = useState([]);
//     const [chatValue, setChatValue] = useState(null);
//     const [receipentId, setReceipentId] = useState(null);
//     const [ws, setWs] = useState(null);
//     const [receipentName, setReceipentName] = useState(null);

//     const account = useSelector((state) => state.account);
//     const { id, token, user } = account;
//     const classes = useStyles();
//     const messagesEndRef = useRef(null);

//     useEffect(() => {
//         messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//     }, [chatMessages]);

//     useEffect(() => {
//         axios.get(configData.API_SERVER + 'chat/chatrooms/')
//             .then((response) => {
//                 setChatRoom(response.data);
//             }).catch((error) => {
//                 console.log(error);
//             });
//     }, []);

//     const handleChatClick = (chat) => {
//         setChatValue(chat);
//         console.log(chat);
//         axios.get(configData.API_SERVER + 'chat/messages/?room_name=' + chat.name)
//         .then((response) => {
//             setChatMessages(response.data);
//         }).catch((error) => {
//             console.log(error);
//         });

//         const [ , name_value] = chat.name.split('_');
//         let receId = null;
//         chat.members.forEach((item) => {
//             if (item.username === name_value) {
//                 receId = item.id;
//                 setReceipentId(item.id);
//                 setReceipentName(item.username)
//             }
//         });

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
//             if(receId == data.user_id){
//                 setChatMessages(prevMessages => [...prevMessages, { content: data.message, user: { id: data.user_id, username: data.username, room_name: data.room_name }  }]);
//             }
//         }
//     };

//     const handleCloseChat = () => {
//         setChatMessages([]);
//         setChatValue(null);
//         if (ws) {
//             ws.close();
//         }
//         setWs(null);
//     };

//     const handleSendMessage = () => {
//         if (message.trim() && chatValue) {
//             const newMessage = {
//                 content: message,
//                 user: { id: id, username: user },
//                 timestamp: new Date().toISOString()
//             };

//             ws.send(JSON.stringify({
//                 'message': message,
//                 'recipient': receipentName,
//                 'currentadmin': user,
//             }));

//             setChatMessages([...chatMessages, newMessage]);
//             setMessage('');
//         }
//     };

//     return (
//         <Grid container spacing={2} style={{ height: '85vh' }}>
//             <Grid item xs={4} style={{ height: '100%', overflowY: 'auto' }}>
//                 <Paper style={{ height: '100%' }}>
//                     <Box p={2} bgcolor={colors.primaryMain}>
//                         <Typography variant="h6" color="black">Chats</Typography>
//                     </Box>
//                     <Divider />
//                     <List>
//                         {chatRoom.map((chat, index) => (
//                             <React.Fragment key={chat.id}>
//                                 <ListItem button onClick={() => handleChatClick(chat)}
//                                 className={chatValue && chatValue.id === chat.id ? classes.selected : null}>
//                                   <ListItemText
//                                     primary={
//                                       <Typography variant="h5" style={{ fontWeight: 'bold' }}>
//                                         {chat.name.split('_')[1].toUpperCase()}
//                                       </Typography>
//                                     }
//                                     secondary={
//                                       <Typography variant="body2" style={{ fontStyle: 'italic' }}>
//                                         Members: {chat.members.map((item) => item.username).join(', ')}
//                                       </Typography>
//                                     }
//                                   />
//                                 </ListItem>
//                                 {index < chatRoom.length - 1 && <Divider />}
//                             </React.Fragment>
//                         ))}
//                     </List>
//                 </Paper>
//             </Grid>
//             <Grid item xs={8} style={{ height: '100%' }}>
//                 <Paper style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
//                     {chatValue ? (
//                         <Box display="flex" flexDirection="column" flexGrow={1} style={{ height: '100%' }}>
//                             <Box display="flex" flexDirection="column" justifyContent="space-between" p={1} borderBottom="1px solid #ccc" bgcolor={colors.primaryMain} fontWeight={600}>
//                                 <Box display="flex" justifyContent="space-between" alignItems="center">
//                                     <Typography variant="h4">{chatValue.name.split('_')[1].toUpperCase()}</Typography>
//                                     <IconButton onClick={handleCloseChat}>
//                                         <CloseIcon />
//                                     </IconButton>
//                                 </Box>
//                                 <Typography variant="body2" style={{ fontStyle: 'italic' }}>
//                                     Members: {chatValue.members.map((item) => item.username).join(', ')}
//                                 </Typography>
//                             </Box>
//                             <Box p={2} flexGrow={1} style={{ overflowY: 'auto' }}>
//                                 {chatMessages.map((msg, index) => (
//                                     <Box key={index} display="flex" flexDirection="column" alignItems={msg.user.id === receipentId ? 'flex-start' : 'flex-end'} >
//                                         <Box
//                                             bgcolor={msg.user.id === receipentId ? '#e0e0e0' : '#ffb108'}
//                                             color={msg.user.id === receipentId ? 'black' : 'white'}
//                                             p={1}
//                                             borderRadius={1}
//                                             maxWidth="70%"
//                                             style={{ wordWrap: 'break-word' }}
//                                         >
//                                             <Typography variant="body2" style={{ fontWeight: 'bold' }}>
//                                                 {msg.user.username}
//                                             </Typography>
//                                             <Typography variant="body1">
//                                                 {msg.content}
//                                             </Typography>
//                                         </Box>
//                                     </Box>
//                                 ))}
//                                 <div ref={messagesEndRef} />
//                             </Box>
//                             <Box display="flex" alignItems="center" p={1} borderTop="1px solid #ccc" bgcolor="#f5f5f5">
//                                 <InputBase
//                                     placeholder="Type a message"
//                                     value={message}
//                                     onChange={(e) => setMessage(e.target.value)}
//                                     fullWidth
//                                     style={{ marginRight: '8px' }}
//                                 />
//                                 <IconButton onClick={handleSendMessage} color="secondary">
//                                     <SendIcon />
//                                 </IconButton>
//                             </Box>
//                         </Box>
//                     ) : (
//                         <Box display="flex" justifyContent="center" alignItems="center" height="100%">
//                             <Typography variant="h4">Select a chat to view the conversation</Typography>
//                         </Box>
//                     )}
//                 </Paper>
//             </Grid>
//         </Grid>
//     );
// };

// export default ChatBoard;


// no pagination file