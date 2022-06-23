import React, { Component } from 'react';
import '../stylesheets/Header.css';

class Header extends Component {
  navTo(uri) {
    window.location.href = window.location.origin + uri;
  }

  render() {
    return (
      <div className='App-header'>
        <h1
          onClick={() => {
            this.navTo('');
          }}
        >
          Udacitrivia
        </h1>
        <h2
          onClick={() => {
            this.navTo('');
          }}
        >
          List
        </h2>
        <h3
          onClick={() => {
            this.navTo('/add-question');
          }}
        >
          Add Question
        </h3>
        <h3
          onClick={() => {
            this.navTo('/add-category');
          }}
        >
          Add Category
        </h3>
        <h2
          onClick={() => {
            this.navTo('/play');
          }}
        >
          Play
        </h2>
      </div>
    );
  }
}

export default Header;
