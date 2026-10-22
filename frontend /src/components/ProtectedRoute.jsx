import {Navigate} from 'react-router-dom';import {useAuth} from '../context/AuthContext.jsx';import {tok} from '../api/client.js';import LoadingSpinner from './LoadingSpinner.jsx';
export default function ProtectedRoute({children}){const {user,ready}=useAuth();
 if(!tok())return <Navigate to="/login" replace/>;if(!ready)return <div className="center-screen"><LoadingSpinner/></div>;
 return user?children:<Navigate to="/login" replace/>;}
