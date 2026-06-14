// src/components/Login.jsx
import { useState } from 'react';
import { login, register } from '../services/api';

function Login({ onLoginSuccess }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isRegister, setIsRegister] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (isRegister) {
                await register(username, password);
                setIsRegister(false);
                setError('Registration successful! Please login.');
            } else {
                const token = await login(username, password);
                localStorage.setItem('token', token);
                localStorage.setItem('username', username);
                onLoginSuccess();
            }
        } catch (err) {
            setError(isRegister ? 'Registration failed' : 'Invalid credentials');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h2>{isRegister ? 'Register' : 'Login'}</h2>
                {error && <p style={styles.error}>{error}</p>}
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        style={styles.input}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        style={styles.input}
                        required
                    />
                    <button type="submit" style={styles.button} disabled={loading}>
                        {loading ? 'Loading...' : (isRegister ? 'Register' : 'Login')}
                    </button>
                </form>
                <p style={styles.toggle}>
                    {isRegister ? 'Already have an account?' : "Don't have an account?"}
                    <button 
                        onClick={() => setIsRegister(!isRegister)} 
                        style={styles.linkButton}
                    >
                        {isRegister ? 'Login' : 'Register'}
                    </button>
                </p>
            </div>
        </div>
    );
}

const styles = {
    container: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#f5f5f5'
    },
    card: {
        padding: '40px',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        width: '300px'
    },
    input: {
        width: '100%',
        padding: '12px',
        marginBottom: '15px',
        border: '1px solid #ddd',
        borderRadius: '4px',
        boxSizing: 'border-box'
    },
    button: {
        width: '100%',
        padding: '12px',
        backgroundColor: '#007bff',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer'
    },
    error: {
        color: 'red',
        marginBottom: '15px'
    },
    toggle: {
        marginTop: '20px',
        textAlign: 'center'
    },
    linkButton: {
        background: 'none',
        border: 'none',
        color: '#007bff',
        cursor: 'pointer',
        marginLeft: '5px'
    }
};

export default Login;
