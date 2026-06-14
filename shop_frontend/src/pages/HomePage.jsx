// src/pages/HomePage.jsx
import { useState, useEffect } from 'react';
import { getHomeRecommendations } from '../services/api';
import ProductCard from '../components/ProductCard';

function HomePage() {
    const [recommendations, setRecommendations] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchRecommendations = async () => {
            try {
                const data = await getHomeRecommendations();                
                console.log('Recommendations data:', data);                
                setRecommendations(data);
            } catch (err) {
                setError('Nie udało się załadować rekomendacji');
            } finally {
                setLoading(false);
            }
        };
        fetchRecommendations();
    }, []);

    if (loading) return <div style={styles.loading}>Ładowanie rekomendacji...</div>;
    if (error) return <div style={styles.error}>{error}</div>;

    return (
        <div style={styles.container}>
            <div style={styles.header}>
                <h1>Witamy ponownie!</h1>
                <p>Na postawie twojej ostatniej aktywności możesz polubić:</p>
                {recommendations?.algorithm && (
                    <span style={styles.algorithm}>
                        Rekomendacje bazujące na algorytmie: {recommendations.algorithm}
                    </span>
                )}
            </div>
            <div style={styles.grid}>
                {
                recommendations?.recommendations?.map((product, index) => (
                    <ProductCard 
                        key={product.parent_asin || `product-${index}`} 
                        product={product}
                        showScore={true}
                        showSimilarity={false}
                        showNumberUsers={true}
                    />
                ))}
            </div>
            {(!recommendations?.recommendations || recommendations.recommendations.length === 0) && (
                <p style={styles.empty}>Brak dostępnych rekomendacji</p>
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
        color: '#666'
    }
};

export default HomePage;
