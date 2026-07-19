import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './Gallery.css';

const Gallery = () => {
  const [images, setImages] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const authHeaders = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  });

  const fetchImages = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        'http://127.0.0.1:8000/history/all',
        authHeaders()
      );
      setImages(Array.isArray(response.data) ? response.data : []);
      setError('');
    } catch (err) {
      if (err.response) {
        setError('Failed to fetch history.');
      } else if (err.request) {
        setError('Network error. Please try again.');
      } else {
        setError('Error: ' + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchImages();
  }, []);

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://127.0.0.1:8000/history/${id}`, authHeaders());
      setImages((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      setError('Could not delete that item.');
    }
  };

  return (
    <div className="image-gallery">
      {error && <p className="error-message">{error}</p>}
      {loading && <p>Loading history...</p>}
      {!loading && !error && images.length === 0 && (
        <p>No searches yet - try a text, image, or video search.</p>
      )}
      <div className="image-grid">
        {images.map((item) => (
          <div key={item.id} className="image-item">
            <img src={item.link} alt={item.item_name} />
            <div className="image-item-info">
              <p className="image-item-name">{item.item_name}</p>
              <button
                className="image-item-delete"
                onClick={() => handleDelete(item.id)}
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Gallery;
