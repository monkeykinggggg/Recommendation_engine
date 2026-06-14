// src/components/ProductCard.jsx
import { Link } from 'react-router-dom';

function ProductCard({ product  , showScore = false, showSimilarity = false, showNumberUsers = false}) {
    return (
        <Link to={`/products/${product.parent_asin}`} style={styles.card}>
            <div style={styles.imageContainer}>
                {product.image_representative ? (
                    <img 
                        src={product.image_representative} 
                        alt={product.title}
                        style={styles.image}
                    />
                ) : (
                    <span style={styles.placeholder}>📦</span>
                )}
            </div>
            <div style={styles.content}>
                <h3 style={styles.title}>{product.title || 'Unknown Product'}</h3>
                {showScore && product.predicted_score && (
                    <p style={styles.score}>
                        Twoja przewidywana ocena produktu: {product.predicted_score.toFixed(2)}
                    </p>
                )}
                {showSimilarity && product.similarity_score && (
                    <p style={styles.similarity}>
                        Podobieństwo produktu do wyszukiwanego: {product.similarity_score.toFixed(2)}%
                    </p>
                )}
                {showNumberUsers && product.similar_users_count && (
                    <p style={styles.similarity}>
                        Liczba użytkowników podobnych (na których oparto rekomendację): {product.similar_users_count}
                    </p>
                )}
            </div>
        </Link>
    );
}

const styles = {
    card: {
        display: 'block',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        overflow: 'hidden',
        textDecoration: 'none',
        color: 'inherit',
        transition: 'transform 0.2s, box-shadow 0.2s'
    },
    imageContainer: {
        height: '200px',
        backgroundColor: '#f0f0f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
    },
    image: {
        maxWidth: '100%',
        maxHeight: '100%',
        objectFit: 'contain'
    },
    placeholder: {
        fontSize: '48px'
    },
    content: {
        padding: '15px'
    },
    title: {
        fontSize: '14px',
        margin: '0 0 10px 0',
        lineHeight: '1.4',
        maxHeight: '40px',
        overflow: 'hidden'
    },
    score: {
        fontSize: '12px',
        color: '#28a745',
        margin: '5px 0'
    },
    similarity: {
        fontSize: '12px',
        color: '#007bff',
        margin: '5px 0'
    }
};

export default ProductCard;
