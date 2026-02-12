import React from 'react';

/**
 * Error boundary for graceful error handling and user feedback.
 * Renders fallback when a child throws; optionally show retry.
 */
export class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    if (typeof this.props.onError === 'function') {
      this.props.onError(error, errorInfo);
    }
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
    this.props.onRetry?.();
  };

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        return typeof this.props.fallback === 'function'
          ? this.props.fallback({ error: this.state.error, retry: this.handleRetry })
          : this.props.fallback;
      }
      return (
        <div className="error-boundary" role="alert">
          <h2 className="error-boundary__title">Something went wrong</h2>
          <p className="error-boundary__message">
            {this.props.message || 'An error occurred. Please try again.'}
          </p>
          {this.props.showRetry && (
            <button type="button" className="btn btn--primary" onClick={this.handleRetry}>
              Try again
            </button>
          )}
        </div>
      );
    }
    return this.props.children;
  }
}
