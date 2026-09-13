import React from 'react';
import { SimplePageChrome } from '@/components/landing/SimplePageChrome';

export function TermsPage() {
  return (
    <SimplePageChrome>
      <div className="legal-page">
        <div className="section-head reveal" style={{ textAlign: 'left', margin: '0 0 8px' }}>
          <span className="section-eyebrow">Legal</span>
          <h2 style={{ marginBottom: 0 }}>Terms of Service</h2>
        </div>
        <p className="legal-meta">Last updated: September 2026</p>

        <div className="legal-section reveal">
          <h3>1. Using LaptopSathi AI</h3>
          <p>
            LaptopSathi AI is an independent, AI-powered laptop recommendation and comparison
            tool. By creating an account or using the site, you agree to the points below.
            This is a small, independently run project — please read this as a plain-language
            summary rather than a dense legal document.
          </p>
          <ul className="legal-list">
            <li>You must be able to form a binding agreement in your jurisdiction to create an account.</li>
            <li>You&apos;re responsible for keeping your login credentials secure and for activity on your account.</li>
            <li>Don&apos;t attempt to scrape, reverse engineer, or abuse the recommendation engine or API.</li>
            <li>Content and recommendations are provided for informational purposes to help you make your own decision.</li>
          </ul>
        </div>

        <div className="legal-section reveal">
          <h3>2. Recommendations aren&apos;t guarantees</h3>
          <ul className="legal-list">
            <li>Laptop specifications, pricing, and availability change often and may not always be current.</li>
            <li>AI-generated recommendations are a decision aid, not professional purchasing advice.</li>
            <li>We don&apos;t accept payment from manufacturers or retailers to influence rankings — but we also can&apos;t guarantee any specific outcome from a purchase you make based on a recommendation.</li>
          </ul>
        </div>

        <div className="legal-section reveal">
          <h3>3. Accounts &amp; acceptable use</h3>
          <ul className="legal-list">
            <li>One account per person; don&apos;t share credentials or create accounts to impersonate someone else.</li>
            <li>We may suspend accounts used for abuse, fraud, or attempts to disrupt the service.</li>
            <li>You can request deletion of your account and associated data at any time.</li>
          </ul>
        </div>

        <div className="legal-section reveal">
          <h3>4. Changes to these terms</h3>
          <p>
            As the product evolves, these terms may be updated. Meaningful changes will be
            reflected by updating the date at the top of this page.
          </p>
        </div>

        <div className="legal-section reveal">
          <h3>5. Contact</h3>
          <p>
            Questions about these terms can be directed to the project maintainer, Harsh,
            through the contact details on the About page.
          </p>
        </div>
      </div>
    </SimplePageChrome>
  );
}
