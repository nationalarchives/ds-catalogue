/**
 * Progressive loading for record detail page components.
 * 
 * Loads non-critical content (related records and subjects enrichment)
 * after the initial page render for better performance.
 */

(function() {
    'use strict';

    // Set cookie to indicate JS is enabled
    document.cookie = 'js_enabled=true; path=/; max-age=31536000; SameSite=Lax';

    // Get configuration from config div
    var configDiv = document.getElementById('progressive-loading-config');
    if (!configDiv) {
        console.error('[Progressive Loading] Configuration not found');
        return;
    }

    // Check if progressive loading is enabled
    var progressiveEnabled = configDiv.getAttribute('data-progressive-loading') === 'true';
    if (!progressiveEnabled) {
        return; // Progressive loading disabled, exit early
    }

    var recordId = configDiv.getAttribute('data-record-id');
    if (!recordId) {
        console.error('[Progressive Loading] No record ID found');
        return;
    }

    // Get URL prefix from data attribute or default to empty string
    // This allows the template to configure the prefix (e.g., '/catalogue/' or '')
    var urlPrefix = configDiv.getAttribute('data-api-prefix') || '';

    /**
     * Fetch and render delivery options
     */
    function loadDeliveryOptions() {
        var container = document.getElementById('delivery-options-container');
        if (!container) {
            return; // Container not found, skip
        }

        var placeholder = document.getElementById('delivery-options-placeholder');
        
        fetch(urlPrefix + '/api/records/' + recordId + '/delivery-options/')
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(function(data) {
                if (!data.success || !data.has_delivery_options) {
                    // No delivery options, hide the section using CSS class
                    container.classList.add('progressive-config-hidden');
                    return;
                }

                // Build HTML for delivery options
                var html = buildDeliveryOptionsHTML(data);
                
                // Replace placeholder with actual content
                if (placeholder) {
                    placeholder.remove();
                }
                container.innerHTML = html;
                container.classList.remove('progressive-config-hidden');
            })
            .catch(function(error) {
                console.error('[Progressive Loading] Failed to load delivery options:', error);
                // Hide the section on error using CSS class
                container.classList.add('progressive-config-hidden');
            });
    }

    /**
     * Build HTML for delivery options
     */
    function buildDeliveryOptionsHTML(data) {
        var html = '<div class="tna-container tna-!--margin-top-m">' +
            '<div class="tna-column tna-column--full tna-margin-top-m">' +
            '<div class="tna-accordion" data-module="tna-accordion" data-accordion-id="record-extended-details-delivery">' +
            '<div class="tna-accordion__item">' +
            '<div class="tna-accordion__heading">' +
            '<button type="button" class="tna-accordion__button" aria-expanded="false">' +
            '<span class="tna-accordion__button-text">' + escapeHTML(data.delivery_options_heading) + '</span>' +
            '<i class="fa-solid fa-chevron-down tna-accordion__icon" aria-hidden="true"></i>' +
            '</button></div>' +
            '<div class="tna-accordion__content" hidden>';

        if (data.delivery_instructions && data.delivery_instructions.length > 0) {
            html += '<ol class="tna-ol">';
            data.delivery_instructions.forEach(function(instruction) {
                html += '<li>' + escapeHTML(instruction) + '</li>';
            });
            html += '</ol>';
        }

        if (data.tna_discovery_link) {
            html += '<div class="tna-button-group tna-!--margin-top-s">' +
                '<a href="' + escapeHTML(data.tna_discovery_link) + '" target="_blank" class="tna-button discovery-link">' +
                'View this record page' +
                '</a></div>';
        }

        html += '</div></div></div></div></div>';
        return html;
    }

    /**
     * Fetch and render related records
     */
    function loadRelatedRecords() {
        var container = document.getElementById('related-records-container');
        if (!container) {
            return; // Container not found, skip
        }

        var placeholder = document.getElementById('related-records-placeholder');
        
        fetch(urlPrefix + '/api/records/' + recordId + '/related/?limit=3')
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(function(data) {
                if (!data.success || !data.related_records || data.related_records.length === 0) {
                    // No related records, hide the section using CSS class
                    container.classList.add('progressive-config-hidden');
                    return;
                }

                // Build HTML for related records
                var html = buildRelatedRecordsHTML(data.related_records);
                
                // Replace placeholder with actual content
                if (placeholder) {
                    placeholder.remove();
                }
                container.innerHTML = html;
                container.classList.remove('progressive-config-hidden');
            })
            .catch(function(error) {
                console.error('[Progressive Loading] Failed to load related records:', error);
                // Hide the section on error using CSS class
                container.classList.add('progressive-config-hidden');
            });
    }

    /**
     * Build HTML for related records
     */
    function buildRelatedRecordsHTML(records) {
        var sectionHTML = '<div class="tna-section tna-background-accent-">' +
            '<div class="tna-container">' +
            '<div class="tna-column tna-column--full tna-!--margin-top-l">' +
            '<h2 class="tna-heading-l">Related records</h2>' +
            '<p>Records that share similar topics with this record.</p>' +
            '</div></div>' +
            '<div class="tna-container related-records">';

        records.forEach(function(record) {
            var description = record.description || '';
            var truncatedDescription = truncateText(stripTags(description), 150);
            
            sectionHTML += 
                '<div class="tna-column tna-column--width-1-3 tna-column--full-small tna-column--full-tiny tna-!--margin-top-m">' +
                '<div class="tna-aside tna-aside--tight tna-background-contrast full-height-aside">' +
                '<hgroup class="tna-hgroup-m">' +
                '<p class="tna-hgroup__supertitle">' + escapeHTML(record.level.toUpperCase()) + '</p>' +
                '<h3 class="tna-hgroup__title">' +
                '<a href="' + escapeHTML(record.url) + '">' + escapeHTML(stripTags(record.summary_title)) + '</a>' +
                '</h3></hgroup>' +
                '<p><strong>Catalogue reference:</strong> ' + escapeHTML(record.reference_number) + '</p>';
            
            if (record.date_covering) {
                sectionHTML += '<p><strong>Date:</strong> ' + escapeHTML(record.date_covering) + '</p>';
            }
            
            if (truncatedDescription) {
                sectionHTML += '<p>' + escapeHTML(truncatedDescription) + '</p>';
            }
            
            sectionHTML += '<p><a href="' + escapeHTML(record.url) + '">See more</a></p>' +
                '</div></div>';
        });

        sectionHTML += '</div></div>';
        return sectionHTML;
    }

    /**
     * Fetch and render subjects enrichment
     */
    function loadSubjectsEnrichment() {
        var container = document.getElementById('subjects-enrichment-container');
        if (!container) {
            return; // Container not found, skip
        }

        var placeholder = document.getElementById('subjects-enrichment-placeholder');
        
        fetch(urlPrefix + '/api/records/' + recordId + '/subjects-enrichment/')
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(function(data) {
                if (!data.success || !data.has_enrichment || !data.html) {
                    // No enrichment data, hide the section using CSS class
                    container.classList.add('progressive-config-hidden');
                    return;
                }
                
                // Replace placeholder with pre-rendered HTML from server
                if (placeholder) {
                    placeholder.remove();
                }
                container.innerHTML = data.html;
                container.classList.remove('progressive-config-hidden');
            })
            .catch(function(error) {
                console.error('[Progressive Loading] Failed to load subjects enrichment:', error);
                // Hide the section on error using CSS class
                container.classList.add('progressive-config-hidden');
            });
    }

    /**
     * Fetch and render available online box
     * Note: Data already fetched in Phase 2, this just re-renders it client-side
     */
    function loadAvailableOnline() {
        var container = document.getElementById('available-online-container');
        if (!container) {
            return;
        }

        var placeholder = document.getElementById('available-online-placeholder');
        
        // Fetch pre-rendered HTML from server (uses Phase 2 data)
        fetch(urlPrefix + '/api/records/' + recordId + '/available-online/')
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(function(data) {
                if (!data.success || !data.has_content || !data.html) {
                    container.classList.add('progressive-config-hidden');
                    return;
                }
                
                if (placeholder) {
                    placeholder.remove();
                }
                container.innerHTML = data.html;
                container.classList.remove('progressive-config-hidden');
            })
            .catch(function(error) {
                console.error('[Progressive Loading] Failed to load available online:', error);
                container.classList.add('progressive-config-hidden');
            });
    }

    /**
     * Fetch and render available in person box
     * Note: Data already fetched in Phase 2, this just re-renders it client-side
     */
    function loadAvailableInPerson() {
        var container = document.getElementById('available-in-person-container');
        if (!container) {
            return;
        }

        var placeholder = document.getElementById('available-in-person-placeholder');
        
        // Fetch pre-rendered HTML from server (uses Phase 2 data)
        fetch(urlPrefix + '/api/records/' + recordId + '/available-in-person/')
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(function(data) {
                if (!data.success || !data.has_content || !data.html) {
                    container.classList.add('progressive-config-hidden');
                    return;
                }
                
                if (placeholder) {
                    placeholder.remove();
                }
                container.innerHTML = data.html;
                container.classList.remove('progressive-config-hidden');
            })
            .catch(function(error) {
                console.error('[Progressive Loading] Failed to load available in person:', error);
                container.classList.add('progressive-config-hidden');
            });
    }

    /**
     * Utility: Strip HTML tags
     */
    function stripTags(html) {
        var div = document.createElement('div');
        div.innerHTML = html;
        return div.textContent || div.innerText || '';
    }

    /**
     * Utility: Truncate text
     */
    function truncateText(text, maxLength) {
        if (text.length <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength) + '...';
    }

    /**
     * Utility: Escape HTML to prevent XSS
     */
    function escapeHTML(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Load progressive content when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            loadAvailableOnline();        // ← ADD
            loadAvailableInPerson();      // ← ADD
            loadRelatedRecords();
            loadSubjectsEnrichment();
        });
    } else {
        // DOM already loaded
        loadAvailableOnline();            // ← ADD
        loadAvailableInPerson();          // ← ADD
        loadRelatedRecords();
        loadSubjectsEnrichment();
    }
})();