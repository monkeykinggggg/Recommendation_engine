// src/components/Navbar.jsx
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';

function Navbar({ onLogout }) {
    const [searchQuery, setSearchQuery] = useState('');
    const navigate = useNavigate();

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        onLogout();
    };

    return (
        <nav style={styles.nav}>
            <Link to="/" style={styles.logo}>Sklep</Link>
            <form onSubmit={handleSearch} style={styles.searchForm}>
                <input
                    type="text"
                    placeholder="Wyszukaj produkt..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={styles.searchInput}
                />
                <button type="submit" style={styles.searchButton}>Szukaj</button>
            </form>
            <div style={styles.userSection}>
                <span style={styles.username}>{localStorage.getItem('username')}</span>
                <button onClick={handleLogout} style={styles.logoutButton}>Wyloguj</button>
            </div>
        </nav>
    );
}

const styles = {
    nav: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '15px 30px',
        backgroundColor: '#333',
        color: 'white'
    },
    logo: {
        fontSize: '24px',
        fontWeight: 'bold',
        color: 'white',
        textDecoration: 'none'
    },
    searchForm: {
        display: 'flex',
        flex: 1,
        maxWidth: '500px',
        margin: '0 30px'
    },
    searchInput: {
        flex: 1,
        padding: '10px',
        border: 'none',
        borderRadius: '4px 0 0 4px'
    },
    searchButton: {
        padding: '10px 20px',
        backgroundColor: '#007bff',
        color: 'white',
        border: 'none',
        borderRadius: '0 4px 4px 0',
        cursor: 'pointer'
    },
    userSection: {
        display: 'flex',
        alignItems: 'center',
        gap: '15px'
    },
    username: {
        color: '#ccc'
    },
    logoutButton: {
        padding: '8px 16px',
        backgroundColor: '#dc3545',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer'
    }
};

export default Navbar;
