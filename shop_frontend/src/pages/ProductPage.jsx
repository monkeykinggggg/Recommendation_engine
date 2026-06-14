// src/pages/ProductPage.jsx
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getProduct, getProductRecommendations } from '../services/api';
import ProductCard from '../components/ProductCard';

function ProductPage() {
    const { productId } = useParams();
    const [product, setProduct] = useState(null);
    const [recommendations, setRecommendations] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [productData, recsData] = await Promise.all([
                    getProduct(productId),
                    getProductRecommendations(productId)
                ]);
                setProduct(productData);
                console.log(productData);
                setRecommendations(recsData);
                setCurrentImageIndex(0);
            } catch (err) {
                setError('Failed to load product');
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [productId]);

    if (loading) return <div style={styles.loading}>Ładowanie produktu...</div>;
    if (error) return <div style={styles.error}>{error}</div>;

    return (
        <div style={styles.container}>
            {/* Product Details */}
            <div style={styles.productSection}>
                <div style={styles.imageSection}>
                    {product.images && product.images.length > 0 ? (
                        <div style={styles.carouselContainer}>
                            {product.images.length > 1 && (
                                <button 
                                    style={styles.arrowButton}
                                    onClick={() => setCurrentImageIndex(prev => 
                                        prev === 0 ? product.images.length - 1 : prev - 1
                                    )}
                                >
                                    ❮
                                </button>
                            )}
                            <img 
                                src={product.images[currentImageIndex]} 
                                alt={`${product.title} - obraz ${currentImageIndex + 1}`}
                                style={styles.productImage}
                            />
                            {product.images.length > 1 && (
                                <button 
                                    style={{...styles.arrowButton, ...styles.arrowRight}}
                                    onClick={() => setCurrentImageIndex(prev => 
                                        prev === product.images.length - 1 ? 0 : prev + 1
                                    )}
                                >
                                    ❯
                                </button>
                            )}
                            {product.images.length > 1 && (
                                <div style={styles.imageCounter}>
                                    {currentImageIndex + 1} / {product.images.length}
                                </div>
                            )}
                        </div>
                    ) : (
                        <div style={styles.imagePlaceholder}>📦</div>
                    )}
                </div>
                <div style={styles.detailsSection}>
                    <h1 style={styles.title}>{product?.title}</h1>
                    <div style={styles.rating}>
                        ⭐ {product?.averageRating?.toFixed(1) || 'N/A'} 
                        ({product?.ratingNumber || 0} reviews)
                    </div>
                    {product?.store && (
                        <p style={styles.store}>Shop: {product.store}</p>
                    )}
                    {product?.features && product.features.length > 0 && (
                        <div style={styles.features}>
                            <h3>Features:</h3>
                            <ul>
                                {product.features.slice(0, 5).map((feature, i) => (
                                    <li key={i}>{feature}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                    {product?.descriptions && product.descriptions.length > 0 && (
                        <div style={styles.description}>
                            <h3>Description:</h3>
                            <p>{product.descriptions[0]}</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Recommendations Section */}
            <div style={styles.recommendationsSection}>
                <h2>Możesz również polubić</h2>
                {recommendations?.algorithm && (
                    <span style={styles.algorithm}>
                        Rekomendacje oparte na algorytmie: {recommendations.algorithm}
                    </span>
                )}
                <div style={styles.grid}>
                    {recommendations?.recommendations?.map((rec, index) => (
                        <ProductCard 
                            key={rec.parent_asin || `rec-${index}`} 
                            product={rec} 
                            showScore={false}
                            showSimilarity={true}
                            showNumberUsers={true}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}

const styles = {
    container: {
        padding: '30px',
        maxWidth: '1200px',
        margin: '0 auto'
    },
    productSection: {
        display: 'flex',
        gap: '40px',
        marginBottom: '50px',
        flexWrap: 'wrap'
    },
    imageSection: {
        flex: '0 0 400px'
    },
    carouselContainer: {
        position: 'relative',
        width: '100%',
        height: '400px',
        backgroundColor: '#f0f0f0',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
    },
    arrowButton: {
        position: 'absolute',
        left: '10px',
        top: '50%',
        transform: 'translateY(-50%)',
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        border: 'none',
        borderRadius: '50%',
        width: '40px',
        height: '40px',
        fontSize: '20px',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
        zIndex: 1,
        transition: 'background-color 0.2s'
    },
    arrowRight: {
        left: 'auto',
        right: '10px'
    },
    imageCounter: {
        position: 'absolute',
        bottom: '10px',
        left: '50%',
        transform: 'translateX(-50%)',
        backgroundColor: 'rgba(0, 0, 0, 0.6)',
        color: 'white',
        padding: '5px 12px',
        borderRadius: '15px',
        fontSize: '14px'
    },
    productImage: {
        width: '100%',
        height: '400px',
        objectFit: 'contain',
        borderRadius: '8px',
        backgroundColor: '#f0f0f0'
    },
    imagePlaceholder: {
        width: '100%',
        height: '400px',
        backgroundColor: '#f0f0f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '100px',
        borderRadius: '8px'
    },
    detailsSection: {
        flex: 1,
        minWidth: '300px'
    },
    title: {
        fontSize: '24px',
        marginBottom: '15px'
    },
    rating: {
        fontSize: '18px',
        marginBottom: '15px',
        color: '#f39c12'
    },
    store: {
        color: '#666',
        marginBottom: '20px'
    },
    features: {
        marginBottom: '20px'
    },
    description: {
        color: '#333'
    },
    recommendationsSection: {
        borderTop: '1px solid #eee',
        paddingTop: '30px'
    },
    algorithm: {
        backgroundColor: '#e9ecef',
        padding: '5px 10px',
        borderRadius: '4px',
        fontSize: '12px',
        marginLeft: '10px'
    },
    grid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '20px',
        marginTop: '20px'
    },
    loading: {
        textAlign: 'center',
        padding: '50px'
    },
    error: {
        textAlign: 'center',
        padding: '50px',
        color: 'red'
    }
};

export default ProductPage;
