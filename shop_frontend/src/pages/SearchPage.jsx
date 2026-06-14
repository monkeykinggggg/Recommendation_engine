// src/pages/SearchPage.jsx
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { searchProducts } from '../services/api';
import ProductCard from '../components/ProductCard';

function SearchPage() {
    const [searchParams] = useSearchParams();
    const query = searchParams.get('q') || '';
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!query) return;
        
        const fetchResults = async () => {
            setLoading(true);
            setError('');
            try {
                const data = await searchProducts(query);
                setResults(data);
                console.log('Search results data:', data);
            } catch (err) {
                setError('Search failed');
            } finally {
                setLoading(false);
            }
        };
        fetchResults();
    }, [query]);

    return (
        <div style={styles.container}>
            <div style={styles.header}>
                {query && <p>Wyniki wyszukiwania dla: "{query}"</p>}
                {results?.algorithm && (
                    <span style={styles.algorithm}>
                        Algorytm wykorzystany do wyszukiwania: {results.algorithm}
                    </span>
                )}
            </div>

            {loading && <div style={styles.loading}>Wyszukiwanie...</div>}
            {error && <div style={styles.error}>{error}</div>}

            {!loading && !error && (
                <div style={styles.grid}>
                    {results?.recommendations?.map((product) => (
                        <ProductCard 
                            key={product.parentAsin} 
                            product={product} 
                            showScore={false}
                            showSimilarity={true}
                            showNumberUsers={false}
                        />
                    ))}
                </div>
            )}

            {!loading && !error && results?.recommendations?.length === 0 && (
                <p style={styles.empty}>Brak produktów dla "{query}"</p>
            )}

            {!query && (
                <p style={styles.empty}>Wpisz frazę, aby wyszukać produkty</p>
            )}
        </div>
    );
}

const styles = {
    container: {
        padding: '30px',
        maxWidth: '1200px',
        margin: '0 auto'
    },
    header: {
        marginBottom: '30px'
    },
    algorithm: {
        backgroundColor: '#e9ecef',
        padding: '5px 10px',
        borderRadius: '4px',
        fontSize: '12px'
    },
    grid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
        gap: '20px'
    },
    loading: {
        textAlign: 'center',
        padding: '50px'
    },
    error: {
        textAlign: 'center',
        padding: '50px',
        color: 'red'
    },
    empty: {
        textAlign: 'center',
        color: '#666',
        padding: '50px'
    }
};

export default SearchPage;
