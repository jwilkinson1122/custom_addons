odoo.define('podiatry_manager.Registries', function(require) {
    'use strict';

    /**
     * This definition contains all the instances of ClassRegistry.
     */

    const ComponentRegistry = require('podiatry_manager.ComponentRegistry');

    return { Component: new ComponentRegistry() };
});
