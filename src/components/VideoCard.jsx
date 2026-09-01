import React from 'react';
import PropTypes from 'prop-types';

const VideoCard = ({ videoLink }) => {
  const getEmbedUrl = (url) => {
    if (!url) return '';

    try {
      const parsedUrl = new URL(url);
      let videoId = '';

      if (parsedUrl.hostname.includes('youtu.be')) {
        videoId = parsedUrl.pathname.split('/').filter(Boolean)[0] || '';
      } else if (parsedUrl.pathname.startsWith('/embed/')) {
        videoId = parsedUrl.pathname.split('/').filter(Boolean)[1] || '';
      } else {
        videoId = parsedUrl.searchParams.get('v') || '';
      }

      return videoId ? `https://www.youtube.com/embed/${videoId}` : url;
    } catch (error) {
      return url;
    }
  };

  const embedUrl = getEmbedUrl(videoLink);

  return (
    <div className="mx-auto mt-4 w-full max-w-4xl">
      <h5 className="mb-4 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
        Let's watch a video
      </h5>
      <div className="aspect-video w-full overflow-hidden rounded-lg bg-black shadow-lg">
        <iframe
          className="h-full w-full"
          src={embedUrl}
          title="YouTube video player"
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        ></iframe>
      </div>
    </div>
  );
};

VideoCard.propTypes = {
  videoLink: PropTypes.string,
};

export default VideoCard;
