import {Routes,Route,Navigate} from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import Landing from './pages/Landing.jsx';import Login from './pages/Login.jsx';import Register from './pages/Register.jsx';
import Dashboard from './pages/Dashboard.jsx';import Transfer from './pages/Transfer.jsx';import History from './pages/History.jsx';import FraudAnalyzer from './pages/FraudAnalyzer.jsx';
const P=(c)=><ProtectedRoute>{c}</ProtectedRoute>;
export default function App(){return(<Routes>
<Route path="/" element={<Landing/>}/><Route path="/login" element={<Login/>}/><Route path="/register" element={<Register/>}/>
<Route path="/dashboard" element={P(<Dashboard/>)}/><Route path="/transfer" element={P(<Transfer/>)}/>
<Route path="/history" element={P(<History/>)}/><Route path="/fraud" element={P(<FraudAnalyzer/>)}/>
<Route path="*" element={<Navigate to="/"/>}/></Routes>);}
